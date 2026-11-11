"""Métricas do sistema em coletores independentes de CPU e GPU."""
import ctypes
from ctypes import wintypes
import math
import os
import shutil
import subprocess
import threading

try:
    import psutil
except ImportError:
    psutil=None


def _windows_cpu_times():
    """Retorna (idle, total); o tempo kernel do Windows já inclui idle."""
    idle,kernel,user=wintypes.FILETIME(),wintypes.FILETIME(),wintypes.FILETIME()
    get_times=ctypes.WinDLL('kernel32',use_last_error=True).GetSystemTimes
    get_times.argtypes=[ctypes.POINTER(wintypes.FILETIME)]*3
    get_times.restype=wintypes.BOOL
    if not get_times(ctypes.byref(idle),ctypes.byref(kernel),ctypes.byref(user)):
        raise ctypes.WinError(ctypes.get_last_error())
    def ticks(value):
        return (value.dwHighDateTime<<32)|value.dwLowDateTime
    return ticks(idle),ticks(kernel)+ticks(user)


class PerformanceMonitor:
    def __init__(self):
        self._stop=threading.Event()
        self._guard=threading.Lock()
        self._cpu=None
        self._cpu_status='waiting'
        self._gpu=None
        self._gpu_kind='GPU'
        self._nvidia=shutil.which('nvidia-smi')
        self._threads=[
            threading.Thread(target=self._cpu_loop,daemon=True,name='rover-cpu'),
            threading.Thread(target=self._gpu_loop,daemon=True,name='rover-gpu'),
        ]
        for thread in self._threads:
            thread.start()

    def _read_cpu(self):
        if psutil is not None:
            try:
                # A janela de amostragem ocorre apenas na thread da CPU.
                value=float(psutil.cpu_percent(interval=.5))
                if math.isfinite(value) and 0<=value<=100:
                    return value
            except Exception:
                # No Windows, ainda funciona se a biblioteca não puder medir.
                pass
        if os.name=='nt':
            try:
                idle_before,total_before=_windows_cpu_times()
                if self._stop.wait(.5):
                    return None
                idle_after,total_after=_windows_cpu_times()
                total=total_after-total_before
                idle=idle_after-idle_before
                if total>0 and 0<=idle<=total:
                    return 100.0*(total-idle)/total
            except (OSError,ValueError):
                pass
        return None

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

    def _cpu_loop(self):
        while not self._stop.is_set():
            try:
                cpu=self._read_cpu()
            except Exception:
                cpu=None
            with self._guard:
                self._cpu=cpu
                self._cpu_status='ok' if cpu is not None else 'unavailable'
            self._stop.wait(.5)

    def _gpu_loop(self):
        while not self._stop.is_set():
            try:
                gpu,kind=self._read_gpu()
            except Exception:
                gpu,kind=None,'GPU'
            with self._guard:
                self._gpu=gpu
                self._gpu_kind=kind
            self._stop.wait(2.0)

    def snapshot(self,fps):
        with self._guard:
            return {'fps':round(fps),'cpu':self._cpu,'cpu_status':self._cpu_status,
                    'gpu':self._gpu,'gpu_kind':self._gpu_kind}

    def close(self):
        self._stop.set()
        for thread in self._threads:
            thread.join(timeout=.75)
