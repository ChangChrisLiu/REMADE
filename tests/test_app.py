import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stderr
from io import StringIO

ROOT = Path(__file__).resolve().parents[1]


class AppTests(unittest.TestCase):
    def test_help_runs_without_camera_model_or_robot_sdks(self):
        result = subprocess.run([sys.executable, str(ROOT / 'REMADEDEMO.py'), '--help'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--sort', result.stdout)
        self.assertIn('--confidence', result.stdout)

    def test_missing_weights_fails_before_opening_any_devices(self):
        result = subprocess.run([sys.executable, str(ROOT / 'REMADEDEMO.py'), '--weights', 'missing-model.pt'],
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Model file not found', result.stderr)

    def test_camera_startup_failure_closes_the_window(self):
        from remade.app import main
        from types import SimpleNamespace
        closed = []
        display = SimpleNamespace(close=lambda: closed.append(True))
        with patch('remade.app.Detector'), patch('remade.app.OpenCVDisplay', return_value=display), \
             patch('remade.app.RealSenseStream', side_effect=RuntimeError('camera unavailable')), \
             redirect_stderr(StringIO()):
            self.assertEqual(main([]), 1)
        self.assertEqual(closed, [True])
