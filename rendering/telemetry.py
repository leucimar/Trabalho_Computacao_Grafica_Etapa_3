"""Amostragem assíncrona: jamais executa subprocessos no loop de quadros."""
import os
import shutil
import subprocess
import threading

try:
    import psutil
except ImportError:
    psutil=None

class PerformanceMonitor:
    def __init__(self):
        self._stop=threading.Event()
        self._guard=threading.Lock()
        self._cpu=None
        self._gpu=None
        self._gpu_kind='GPU'
        self._nvidia=shutil.which('nvidia-smi')
        if psutil is not None:
            psutil.cpu_percent(interval=None)
        self._thread=threading.Thread(target=self._run,daemon=True,name='rover-telemetry')
        self._thread.start()

    def _read_gpu(self):
        flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
        if self._nvidia:
            try:
                out=subprocess.run([self._nvidia,'--query-gpu=utilization.gpu',
                                    '--format=csv,noheader,nounits'],capture_output=True,
                                   text=True,encoding='utf-8',errors='replace',timeout=2.0,creationflags=flags)
                if out.returncode==0:
                    values=[float(v.strip()) for v in out.stdout.splitlines() if v.strip()]
                    if values:return max(0.,min(100.,max(values))), 'GPU (NVIDIA)'
            except (OSError,ValueError,subprocess.TimeoutExpired):pass
        if os.name=='nt':
            # Fallback é o motor gráfico mais utilizado, NÃO utilização global.
            command=("$ErrorActionPreference='Stop';"
                     "$s=(Get-Counter '\\GPU Engine(*)\\Utilization Percentage').CounterSamples;"
                     "$v=@($s | ForEach-Object {$_.CookedValue} | Where-Object {$_ -ge 0});"
                     "if($v.Count -gt 0){($v|Measure-Object -Maximum).Maximum}")
            try:
                out=subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command',command],
                                   capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=3.,creationflags=flags)
                if out.returncode==0 and out.stdout.strip():
                    value=float(out.stdout.strip().splitlines()[-1].replace(',','.'))
                    return max(0.,min(100.,value)), 'GPU motor*'
            except (OSError,ValueError,subprocess.TimeoutExpired):pass
        return None,'GPU'

    def _run(self):
        while not self._stop.is_set():
            cpu=psutil.cpu_percent(interval=.15) if psutil else None
            gpu,kind=self._read_gpu()
            with self._guard:
                self._cpu=cpu
                self._gpu=gpu
                self._gpu_kind=kind
            self._stop.wait(2.0)

    def snapshot(self,fps):
        with self._guard:
            return {'fps':round(fps), 'cpu':self._cpu,'gpu':self._gpu,
                    'gpu_kind':self._gpu_kind}

    def close(self):
        self._stop.set()
