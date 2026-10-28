"""Application integration: real runtime modules, simulated device/SDK edges.

No socket, camera, serial device, model checkpoint or GUI is opened here.
"""

from contextlib import ExitStack, redirect_stderr, redirect_stdout
from io import StringIO
import re
import struct
import threading
import time
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import numpy as np

from remade.app import main
from remade.config import CLASS_NAMES, HIGH_BIN, HOME, LOW_BIN


class DeviceBoundary:
    def __init__(self, class_id=2, failure=None, sorting=True):
        self.class_id, self.failure, self.sorting = class_id, failure, sorting
        self.events, self.moves, self.writes, self.frames = [], [], [], []
        self.pose = np.array(HOME)
        self.buffer = bytearray()
        self.frame_number = self.releases = self.busy_frames = self.discards = 0
        self.camera_starts = self.camera_closes = self.window_closes = 0
        self.model_loads = self.robot_connections = self.serial_connections = 0
        self.socket_closed = self.serial_closed = False
        self.grip_started, self.allow_grip = threading.Event(), threading.Event()
        self.deadline = time.monotonic() + 5
        self.status = ''

    def pipeline_start(self, config):
        self.camera_starts += 1

    def pipeline_stop(self):
        self.camera_closes += 1

    def capture(self, timeout):
        if self.failure == 'camera':
            raise RuntimeError('simulated camera failure')
        # Let the real worker run; completion is controlled by events/status,
        # never by assuming a particular frame number or thread schedule.
        threading.Event().wait(.001)
        self.frame_number += 1
        frame = np.full((4, 4, 3), self.frame_number % 255, dtype=np.uint8)
        return NS(get_color_frame=lambda: NS(get_data=lambda: frame))

    def discard(self):
        self.discards += 1
        return False

    def load_model(self, weights):
        self.model_loads += 1
        return NS(names=CLASS_NAMES, predict=self.predict)

    def predict(self, frame, **kwargs):
        if self.failure == 'inference':
            raise RuntimeError('simulated inference failure')
        self.events.append('inference')
        def tensor(values):
            return NS(cpu=lambda: NS(numpy=lambda: np.asarray(values)))
        # The preparation frame deliberately has a different location and
        # class. It must never be used for picking after homing.
        first = self.frame_number == 1 and self.sorting
        boxes = NS(xywh=tensor([[100, 100, 20, 20] if first else [960, 540, 20, 20]]),
                   cls=tensor([4 if first else self.class_id]), conf=tensor([.99]))
        return [NS(boxes=boxes, plot=lambda **kwargs: frame.copy())]

    def overlay(self, frame, text, *args):
        self.status = text.split(' | ')[0]
        self.frames.append((self.frame_number, self.status))

    def key(self, delay):
        if time.monotonic() > self.deadline:
            self.allow_grip.set()
            raise TimeoutError('simulated workflow did not finish')
        if not self.sorting:
            return ord('q') if len(self.frames) >= 4 else -1
        if self.grip_started.is_set() and not self.allow_grip.is_set():
            self.busy_frames += 1
            if self.busy_frames >= 3:
                self.allow_grip.set()
        return ord('q') if self.releases >= 3 and self.status == 'READY' else -1

    def close_window(self):
        self.window_closes += 1

    def connect_socket(self, address, timeout):
        self.robot_connections += 1
        self.events.append('robot connect')
        return self

    def settimeout(self, timeout):
        pass

    def recv(self, count):
        if self.failure == 'robot':
            raise ConnectionError('simulated robot failure')
        if not self.buffer:
            packet = bytearray(1108)
            packet[:4] = struct.pack('!I', len(packet))
            packet[444:492] = struct.pack('!6d', *self.pose)
            self.buffer.extend(packet)
            self.events.append('robot state')
        # Exercise the real fragmented-packet decoder.
        data = bytes(self.buffer[:min(count, 31)])
        del self.buffer[:len(data)]
        return data

    def sendall(self, data):
        command = data.decode('ascii')
        if command.startswith('movel'):
            self.pose = np.array([float(value) for value in re.search(r'p\[([^]]+)\]', command)[1].split(',')])
            self.moves.append(self.pose.copy())
            self.events.append(('move', self.pose.copy()))
        else:
            self.events.append('stop')

    def close(self):
        self.socket_closed = True

    def serial_factory(self, **kwargs):
        self.serial_options = kwargs
        return NS(connect=self.connect_serial, close=self.close_serial,
                  read_holding_registers=self.read_register, write_registers=self.write_registers)

    def connect_serial(self):
        self.serial_connections += 1
        return True

    def close_serial(self):
        self.serial_closed = True

    def read_register(self, **kwargs):
        self.events.append('vacuum read')
        return NS(isError=lambda: self.failure == 'vacuum prepare', registers=[500])

    def write_registers(self, **kwargs):
        values = kwargs['values']
        self.writes.append(values)
        self.events.append(('vacuum', values))
        if values[0]:
            if self.failure != 'vacuum grip':
                self.grip_started.set()
                if not self.allow_grip.wait(3):
                    raise TimeoutError('monitor stopped refreshing during grip')
        else:
            self.releases += 1
        return NS(isError=lambda: bool(values[0]) and self.failure == 'vacuum grip')

    def run(self):
        camera = NS(pipeline=lambda: NS(start=self.pipeline_start, stop=self.pipeline_stop,
                    wait_for_frames=self.capture, poll_for_frames=self.discard),
                    config=lambda: NS(enable_stream=lambda *args: None),
                    stream=NS(color=1), format=NS(bgr8=1))
        cv2 = NS(WINDOW_NORMAL=0, FONT_HERSHEY_SIMPLEX=0, WND_PROP_VISIBLE=0,
                 namedWindow=lambda *args: None, resizeWindow=lambda *args: None,
                 putText=self.overlay, imshow=lambda *args: None, waitKey=self.key,
                 getWindowProperty=lambda *args: 1, destroyAllWindows=self.close_window)
        modules = {'pyrealsense2': camera, 'cv2': cv2, 'ultralytics': NS(YOLO=self.load_model),
                   'pymodbus': NS(), 'pymodbus.client': NS(),
                   'pymodbus.client.sync': NS(ModbusSerialClient=self.serial_factory)}
        self.output = StringIO()
        with ExitStack() as stack:
            stack.enter_context(patch.dict('sys.modules', modules))
            stack.enter_context(patch('remade.robot.socket.create_connection', side_effect=self.connect_socket))
            stack.enter_context(patch('remade.robot.select.select', return_value=([], [], [])))
            stack.enter_context(redirect_stdout(self.output))
            stack.enter_context(redirect_stderr(self.output))
            return main(['--sort', '--serial-device', 'simulated-serial'] if self.sorting else [])


class WorkflowTests(unittest.TestCase):
    def test_all_classes_complete_the_real_application_chain(self):
        for class_id in CLASS_NAMES:
            with self.subTest(class_id=class_id):
                device = DeviceBoundary(class_id)
                self.assertEqual(device.run(), 0, device.output.getvalue())
                self.assertEqual(len(device.moves), 8)  # Initial home plus seven pick/place/home moves.
                np.testing.assert_allclose(device.moves[0], HOME)
                np.testing.assert_allclose(device.moves[1][:3], [.51777396, -.42458136, .15], atol=1e-8)
                self.assertAlmostEqual(device.moves[2][2], -.005)
                destination = HIGH_BIN if class_id in (2, 4) else LOW_BIN
                np.testing.assert_allclose(device.moves[5][:3], [*destination[:2], .1])
                np.testing.assert_allclose(device.moves[-1], HOME)
                self.assertEqual(device.writes, [[0, 0], [316, 316], [0, 0], [0, 0]])
                # Inference deliberately continues on another thread and may
                # interleave between a state read and the vacuum command.
                control_events = [item for item in device.events
                                  if not isinstance(item, str) or item != 'inference']
                release = [i for i, item in enumerate(control_events)
                           if isinstance(item, tuple) and item[0] == 'vacuum' and item[1] == [0, 0]][1]
                # The last confirmed state is read before the destination release.
                self.assertEqual(control_events[release - 1], 'robot state')
                first_move = next(i for i, item in enumerate(device.events) if isinstance(item, tuple))
                self.assertLess(device.events.index('vacuum read'), first_move)
                self.assertLess(device.events.index('inference'), device.events.index('robot connect'))
                self.assertEqual(device.busy_frames, 3)
                self.assertGreaterEqual(device.discards, 2)
                self.assertEqual((device.model_loads, device.camera_starts, device.robot_connections,
                                  device.serial_connections), (1, 1, 1, 1))
                self.assertEqual((device.camera_closes, device.window_closes), (1, 1))
                self.assertTrue(device.socket_closed and device.serial_closed)
                self.assertEqual(device.events[-1], 'stop')

    def test_preparation_failures_never_move_or_release(self):
        for failure in ('camera', 'inference', 'robot', 'vacuum prepare'):
            with self.subTest(failure=failure):
                device = DeviceBoundary(failure=failure)
                self.assertEqual(device.run(), 1)
                self.assertIn('simulated' if failure != 'vacuum prepare' else 'startup register', device.output.getvalue())
                self.assertEqual(device.moves, [])
                self.assertEqual(device.writes, [])
                self.assertEqual((device.camera_closes, device.window_closes), (1, 1))
                if device.robot_connections:
                    self.assertTrue(device.socket_closed)
                if device.serial_connections:
                    self.assertTrue(device.serial_closed)

    def test_failed_grip_prevents_descent_and_does_not_release_on_shutdown(self):
        device = DeviceBoundary(failure='vacuum grip')
        self.assertEqual(device.run(), 1)
        self.assertEqual(len(device.moves), 2)  # Home, then approach; no descent.
        self.assertEqual(device.writes, [[0, 0], [316, 316]])
        self.assertTrue(device.socket_closed and device.serial_closed)
        self.assertEqual((device.camera_closes, device.window_closes), (1, 1))

    def test_monitor_only_never_connects_robot_or_serial(self):
        device = DeviceBoundary(sorting=False)
        self.assertEqual(device.run(), 0)
        self.assertEqual((device.robot_connections, device.serial_connections), (0, 0))
        self.assertEqual(len(device.frames), 4)
        self.assertEqual((device.camera_closes, device.window_closes), (1, 1))
