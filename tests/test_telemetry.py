"""Testes da telemetria sem depender de janela OpenGL."""
import unittest
import subprocess
from unittest.mock import patch
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

if __name__=='__main__': unittest.main()
