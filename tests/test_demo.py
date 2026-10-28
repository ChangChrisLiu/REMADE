import importlib
import socket
import struct
import unittest
from unittest.mock import patch


class DemoTests(unittest.TestCase):
    def test_fragment_receives_share_one_absolute_deadline(self):
        from remade.robot import read_tcp_pose
        clock = [0.0]
        timeouts = []
        class Connection:
            def settimeout(self, timeout):
                timeouts.append(timeout)
            def recv(self, count):
                if count == 4:
                    clock[0] = .8
                    return struct.pack('!I', 492)
                clock[0] = 1.1
                return bytes(count)
        with patch('remade.robot.time.monotonic', side_effect=lambda: clock[0]):
            with self.assertRaises(TimeoutError):
                read_tcp_pose(Connection(), timeout=1)
        self.assertAlmostEqual(timeouts[0], 1)
        self.assertAlmostEqual(timeouts[1], .2)

    def test_import_does_not_connect_to_robot(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('network during import')):
            module = importlib.import_module('REMADEDEMO')
            importlib.reload(module)

    def test_fragmented_tcp_packet_is_read_completely(self):
        from REMADEDEMO import read_tcp_pose
        packet = bytearray(1108)
        packet[:4] = struct.pack('!I', 1108)
        packet[444:492] = struct.pack('!6d', 1, 2, 3, 4, 5, 6)
        class Connection:
            def settimeout(self, timeout):
                pass
            def recv(self, count):
                result = bytes(packet[:min(count, 13)])
                del packet[:len(result)]
                return result
        self.assertEqual(read_tcp_pose(Connection()).tolist(), [1, 2, 3, 4, 5, 6])

    def test_closed_tcp_connection_raises_instead_of_looping(self):
        from REMADEDEMO import read_tcp_pose
        class Connection:
            def settimeout(self, timeout):
                pass
            def recv(self, count):
                return b''
        with self.assertRaises(ConnectionError):
            read_tcp_pose(Connection())


if __name__ == '__main__':
    unittest.main()
