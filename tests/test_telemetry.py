"""Testes da telemetria sem depender de janela OpenGL."""
import unittest
import subprocess
import threading
import time
from unittest.mock import Mock, patch
from rendering.telemetry import PerformanceMonitor

class TelemetryTests(unittest.TestCase):
    def test_unavailable_gpu_is_explicit(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        monitor._nvidia=None
        with patch('rendering.telemetry.os.name','posix'):
            result,source=monitor._read_gpu()
        self.assertIsNone(result)
        self.assertEqual(source,'GPU')

    def test_nvidia_gpu_uses_actual_reported_value(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        monitor._nvidia='nvidia-smi'
        result=type('Result',(),{'returncode':0,'stdout':'42\n'})()
        with patch('rendering.telemetry.subprocess.run',return_value=result):
            value,source=monitor._read_gpu()
        self.assertEqual(value,42.0)
        self.assertEqual(source,'GPU (NVIDIA)')

    def test_windows_counter_after_nvidia_timeout(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        monitor._nvidia='nvidia-smi'
        result=type('Result',(),{'returncode':0,'stdout':'17,5\n'})()
        with patch('rendering.telemetry.os.name','nt'), patch(
                'rendering.telemetry.subprocess.run',
                side_effect=[subprocess.TimeoutExpired('nvidia-smi',2),result]) as run:
            value,source=monitor._read_gpu()
        self.assertEqual(value,17.5)
        self.assertEqual(source,'GPU motor*')
        self.assertEqual(run.call_count,2)
        self.assertEqual(run.call_args.kwargs['errors'],'replace')

    def test_invalid_nvidia_output_is_unavailable(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        monitor._nvidia='nvidia-smi'
        result=type('Result',(),{'returncode':0,'stdout':'N/A\n'})()
        with patch('rendering.telemetry.os.name','posix'), patch(
                'rendering.telemetry.subprocess.run',return_value=result):
            self.assertEqual(monitor._read_gpu(),(None,'GPU'))

    def test_multiple_gpus_report_busiest_device(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        monitor._nvidia='nvidia-smi'
        result=type('Result',(),{'returncode':0,'stdout':'21\n78\n'})()
        with patch('rendering.telemetry.subprocess.run',return_value=result):
            self.assertEqual(monitor._read_gpu(),(78.0,'GPU (NVIDIA)'))

    def test_windows_counter_timeout_is_unavailable(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        monitor._nvidia=None
        with patch('rendering.telemetry.os.name','nt'), patch(
                'rendering.telemetry.subprocess.run',
                side_effect=subprocess.TimeoutExpired('powershell',3)):
            self.assertEqual(monitor._read_gpu(),(None,'GPU'))

    def test_cpu_uses_a_measured_interval(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        with patch('rendering.telemetry.psutil') as sensor:
            sensor.cpu_percent.return_value=23.75
            self.assertEqual(monitor._read_cpu(),23.75)
            sensor.cpu_percent.assert_called_once_with(interval=.5)

    def test_windows_cpu_without_psutil(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        monitor._stop=Mock()
        monitor._stop.wait.return_value=False
        with patch('rendering.telemetry.psutil',None), patch(
                'rendering.telemetry.os.name','nt'), patch(
                'rendering.telemetry._windows_cpu_times',
                side_effect=[(100,400),(175,500)]):
            self.assertEqual(monitor._read_cpu(),25.0)

    def test_windows_cpu_fallback_when_psutil_fails(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        monitor._stop=Mock()
        monitor._stop.wait.return_value=False
        with patch('rendering.telemetry.psutil') as sensor, patch(
                'rendering.telemetry.os.name','nt'), patch(
                'rendering.telemetry._windows_cpu_times',
                side_effect=[(100,400),(150,500)]):
            sensor.cpu_percent.side_effect=OSError('sensor unavailable')
            self.assertEqual(monitor._read_cpu(),50.0)

    def test_invalid_cpu_counter_is_unavailable(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        monitor._stop=Mock()
        monitor._stop.wait.return_value=False
        with patch('rendering.telemetry.psutil',None), patch(
                'rendering.telemetry.os.name','nt'), patch(
                'rendering.telemetry._windows_cpu_times',
                side_effect=[(100,400),(175,400)]):
            self.assertIsNone(monitor._read_cpu())

    def test_missing_cpu_source_does_not_invent_zero(self):
        monitor=PerformanceMonitor.__new__(PerformanceMonitor)
        with patch('rendering.telemetry.psutil',None), patch(
                'rendering.telemetry.os.name','posix'):
            self.assertIsNone(monitor._read_cpu())

    def test_cpu_updates_while_gpu_is_blocked(self):
        release=threading.Event()
        started=threading.Event()
        def slow_gpu():
            started.set()
            release.wait(3)
            return 64.0,'GPU (NVIDIA)'
        with patch.object(PerformanceMonitor,'_read_cpu',return_value=37.25), patch.object(
                PerformanceMonitor,'_read_gpu',side_effect=slow_gpu):
            monitor=PerformanceMonitor()
            try:
                self.assertTrue(started.wait(1))
                deadline=time.monotonic()+2
                while monitor.snapshot(60)['cpu'] is None and time.monotonic()<deadline:
                    time.sleep(.01)
                data=monitor.snapshot(60)
                self.assertEqual(data['cpu'],37.25)
                self.assertEqual(data['cpu_status'],'ok')
                self.assertIsNone(data['gpu'])
                self.assertFalse(release.is_set())
            finally:
                release.set()
                monitor.close()
            self.assertTrue(all(not t.is_alive() for t in monitor._threads))

    def test_cpu_worker_recovers_after_a_read_failure(self):
        with patch.object(PerformanceMonitor,'_read_cpu',side_effect=[
                RuntimeError('temporary failure'),18.5,18.5]), patch.object(
                PerformanceMonitor,'_read_gpu',return_value=(None,'GPU')):
            monitor=PerformanceMonitor()
            try:
                deadline=time.monotonic()+2
                while monitor.snapshot(60)['cpu'] is None and time.monotonic()<deadline:
                    time.sleep(.01)
                self.assertEqual(monitor.snapshot(60)['cpu'],18.5)
            finally:
                monitor.close()

if __name__=='__main__': unittest.main()
