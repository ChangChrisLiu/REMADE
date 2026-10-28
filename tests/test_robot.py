import threading
import socket
import struct
import unittest
from unittest.mock import patch
import numpy as np
from remade.robot import Sorter, URSocket
from remade.config import Settings
from remade.monitor import StopRequested


class RobotTests(unittest.TestCase):
    def test_failed_vacuum_preflight_prevents_first_motion(self):
        from unittest.mock import Mock
        arm, vacuum = Mock(), Mock()
        vacuum.prepare.side_effect = ConnectionError('gripper unavailable')
        sorter = Sorter(arm, vacuum, threading.Event())
        with self.assertRaisesRegex(ConnectionError, 'gripper unavailable'):
            sorter.home()
        arm.pose.assert_called_once()
        arm.move.assert_not_called()
        vacuum.off.assert_not_called()

    def test_state_reads_reuse_connection_and_drain_older_packets(self):
        arm = URSocket(Settings(), threading.Event())
        reader, writer = socket.socketpair()
        reader.settimeout(1)
        arm.command_socket = reader
        def packet(x):
            data = bytearray(1108)
            data[:4] = struct.pack('!I', 1108)
            data[444:492] = struct.pack('!6d', x, 0, 0, 0, 0, 0)
            return data
        try:
            writer.sendall(packet(1) + packet(2))
            with patch('remade.robot.socket.create_connection', side_effect=AssertionError('connection churn')):
                self.assertEqual(arm.pose()[0], 2)
        finally:
            reader.close()
            writer.close()

    def test_release_occurs_after_drop_pose_and_input_does_not_mutate(self):
        events = []
        class Arm:
            def pose(self):
                return np.zeros(6)
            def move(self, pose):
                events.append(('move', list(pose)))
            def close(self):
                pass
        class Vacuum:
            def prepare(self):
                pass
            def on(self):
                events.append(('on', None))
            def off(self):
                events.append(('off', None))
            def close(self):
                pass
        targets = np.array([[2., 100., 200.]])
        sorter = Sorter(Arm(), Vacuum(), threading.Event())
        with patch('remade.robot.detections_to_poses', return_value=np.array([[2., .4, -.3, 0, 2.18, -2.20, .06]])):
            sorter.sort(targets)
        release = next(i for i, event in enumerate(events) if event[0] == 'off')
        self.assertEqual(events[release-1][0], 'move')
        self.assertAlmostEqual(events[release-1][1][2], .1)
        np.testing.assert_array_equal(targets, [[2, 100, 200]])

    def test_stop_prevents_any_new_motion(self):
        stop = threading.Event()
        stop.set()
        arm = URSocket(Settings(), stop)
        with self.assertRaises(StopRequested):
            arm.move([0, 0, 0, 0, 0, 0])

    def test_unreachable_pose_times_out(self):
        arm = URSocket(Settings(motion_timeout=0.005), threading.Event())
        commands = []
        arm.command_socket = type('Connection', (), {'sendall': lambda self, data: commands.append(data)})()
        with patch.object(arm, 'pose', return_value=np.zeros(6)):
            with self.assertRaises(TimeoutError):
                arm.move([1, 1, 1, 0, 0, 0])
        # No monitor or GUI thread participates: the worker must stop immediately.
        self.assertEqual(commands[-1], b'stopl(1.0)\n')

    def test_failed_state_read_stops_before_propagating_error(self):
        arm = URSocket(Settings(), threading.Event())
        commands = []
        arm.command_socket = type('Connection', (), {'sendall': lambda self, data: commands.append(data)})()
        with patch.object(arm, 'pose', side_effect=ConnectionError('state lost')):
            with self.assertRaisesRegex(ConnectionError, 'state lost'):
                arm.move([1, 1, 1, 0, 0, 0])
        self.assertEqual(commands[-1], b'stopl(1.0)\n')
