import threading
import unittest
from types import SimpleNamespace

from remade.monitor import run_monitor


class Camera:
    def __init__(self):
        self.frames = 0
        self.closed = False
        self.discards = 0

    def read(self):
        self.frames += 1
        return self.frames

    def discard_pending(self):
        self.discards += 1

    def close(self):
        self.closed = True


class Display:
    def __init__(self, count=5, callback=None):
        self.frames = []
        self.closed = False
        self.count = count
        self.callback = callback

    def show(self, frame, status):
        self.frames.append(frame)
        if self.callback:
            self.callback(len(self.frames))
        return len(self.frames) < self.count

    def close(self):
        self.closed = True


def detect(frame):
    return SimpleNamespace(frame=frame, targets=[[2, frame, 10]])


class MonitorTests(unittest.TestCase):
    def test_worker_keyboard_interrupt_does_not_repeat_a_completed_future(self):
        from concurrent.futures import Future
        from unittest.mock import Mock, patch
        executor = Mock()
        executor.shutdown.side_effect = [None, AssertionError('shutdown repeated')]
        future = Future()
        future.set_exception(KeyboardInterrupt())
        executor.submit.return_value = future
        robot, camera, display = Mock(), Camera(), Display(count=1)
        with patch('remade.monitor.ThreadPoolExecutor', return_value=executor):
            with self.assertRaises(KeyboardInterrupt):
                run_monitor(camera, detect, display, robot)
        self.assertEqual(executor.shutdown.call_count, 1)
        robot.close.assert_called_once()
        self.assertTrue(camera.closed and display.closed)

    def test_interrupt_during_worker_shutdown_still_closes_resources(self):
        from unittest.mock import Mock, patch
        executor = Mock()
        executor.shutdown.side_effect = [KeyboardInterrupt(), None]
        executor.submit.return_value.done.return_value = False
        robot, camera, display = Mock(), Camera(), Display(count=1)
        with patch('remade.monitor.ThreadPoolExecutor', return_value=executor):
            with self.assertRaises(KeyboardInterrupt):
                run_monitor(camera, detect, display, robot)
        self.assertEqual(executor.shutdown.call_count, 2)
        robot.close.assert_called_once()
        self.assertTrue(camera.closed and display.closed)

    def test_preview_continues_for_multiple_frames_and_closes(self):
        camera, display = Camera(), Display()
        run_monitor(camera, detect, display)
        self.assertEqual(display.frames, [1, 2, 3, 4, 5])
        self.assertTrue(camera.closed and display.closed)

    def test_camera_and_display_close_on_inference_failure(self):
        camera, display = Camera(), Display()
        def fail(frame):
            raise ValueError('bad frame')
        with self.assertRaisesRegex(ValueError, 'bad frame'):
            run_monitor(camera, fail, display)
        self.assertTrue(camera.closed and display.closed)

    def test_frames_continue_while_robot_is_busy_without_queuing_batches(self):
        started, release = threading.Event(), threading.Event()
        ready_seen = threading.Event()
        batches = []
        camera = Camera()
        class Robot:
            def home(self):
                pass
            def sort(self, targets):
                batches.append(targets)
                started.set()
                if not release.wait(2):
                    raise RuntimeError('display did not continue')
            def close(self):
                self.closed = True
        robot = Robot()
        original_read = camera.read
        def read_after_submission():
            if ready_seen.is_set():
                self.assertTrue(started.wait(2))
            return original_read()
        camera.read = read_after_submission
        class BusyDisplay(Display):
            busy_frames = 0
            def show(self, frame, status):
                self.frames.append(frame)
                if status == 'READY':
                    ready_seen.set()
                if started.is_set():
                    self.busy_frames += 1
                if self.busy_frames == 5:
                    release.set()
                    return False
                return True
        display = BusyDisplay()
        try:
            run_monitor(camera, detect, display, robot)
        finally:
            release.set()
        self.assertGreaterEqual(len(display.frames), 6)
        self.assertEqual(display.busy_frames, 5)
        self.assertEqual(len(batches), 1)
        self.assertGreaterEqual(camera.discards, 1)
        self.assertTrue(robot.closed)

    def test_no_targets_never_starts_a_sort(self):
        class Robot:
            def home(self):
                pass
            def sort(self, targets):
                raise AssertionError('empty batch')
            def close(self):
                pass
        run_monitor(Camera(), lambda f: SimpleNamespace(frame=f, targets=[]), Display(), Robot())

    def test_robot_error_is_reported_and_all_resources_close(self):
        class Robot:
            closed = False
            def home(self):
                raise RuntimeError('robot unavailable')
            def close(self):
                self.closed = True
        robot, camera, display = Robot(), Camera(), Display()
        with self.assertRaisesRegex(RuntimeError, 'robot unavailable'):
            run_monitor(camera, detect, display, robot)
        self.assertTrue(camera.closed and display.closed and robot.closed)

    def test_home_finishing_during_inference_does_not_reuse_that_frame(self):
        release_home, home_returning, sorted_once = threading.Event(), threading.Event(), threading.Event()
        selections = []
        class Robot:
            def home(self):
                if not release_home.wait(2):
                    raise RuntimeError('inference never started')
                home_returning.set()
            def sort(self, targets):
                selections.append(targets[0][1])
                sorted_once.set()
            def close(self):
                pass
        def inference(frame):
            if frame == 1:
                release_home.set()
                self.assertTrue(home_returning.wait(2))
            return detect(frame)
        class UntilSorted(Display):
            def show(self, frame, status):
                self.frames.append(frame)
                return not sorted_once.is_set()
        run_monitor(Camera(), inference, UntilSorted(), Robot())
        self.assertTrue(selections)
        self.assertNotIn(1, selections)


if __name__ == '__main__':
    unittest.main()
