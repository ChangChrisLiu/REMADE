"""UR TCP transport and the original DEMO pick/place sequence."""

import socket
import select
import struct
import time
from contextlib import suppress
import numpy as np
from .config import HOME, HIGH_BIN, LOW_BIN, HIGH_VALUE_CLASSES, LOW_VALUE_CLASSES
from .geometry import detections_to_poses, rotation_error
from .monitor import StopRequested


def read_tcp_pose(connection, timeout=3.0):
    deadline = time.monotonic() + timeout
    def exact(size):
        data = bytearray()
        while len(data) < size:
            if time.monotonic() >= deadline:
                raise TimeoutError('robot state packet did not arrive before the deadline')
            chunk = connection.recv(size - len(data))
            if not chunk:
                raise ConnectionError('robot closed the state connection')
            data.extend(chunk)
        return bytes(data)
    size_bytes = exact(4)
    size = struct.unpack('!I', size_bytes)[0]
    if not 492 <= size <= 16384:
        raise ValueError(f'unsupported UR state packet size: {size}')
    packet = size_bytes + exact(size - 4)
    pose = np.asarray(struct.unpack('!6d', packet[444:492]))
    if not np.isfinite(pose).all():
        raise ValueError('robot reported a non-finite TCP pose')
    return pose


class URSocket:
    def __init__(self, settings, stop_event):
        self.settings = settings
        self.stop_event = stop_event
        self.command_socket = None

    def check_stop(self):
        if self.stop_event.is_set():
            raise StopRequested('monitor requested a stop')

    def connect(self):
        self.check_stop()
        if self.command_socket is None:
            self.command_socket = socket.create_connection(
                (self.settings.host, self.settings.port), self.settings.socket_timeout)

    def pose(self):
        self.connect()
        deadline = time.monotonic() + self.settings.socket_timeout
        while True:
            self.check_stop()
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('could not obtain a current robot state packet')
            self.command_socket.settimeout(remaining)
            try:
                pose = read_tcp_pose(self.command_socket, remaining)
            finally:
                self.command_socket.settimeout(self.settings.socket_timeout)
            if not select.select([self.command_socket], [], [], 0)[0]:
                return pose

    def move(self, target):
        self.check_stop()
        target = np.asarray(target, dtype=float)
        if target.shape != (6,) or not np.isfinite(target).all():
            raise ValueError('target pose must contain six finite values')
        self.connect()
        pose_text = ','.join(f'{value:.10f}' for value in target)
        command = f'movel(p[{pose_text}],a={self.settings.acceleration},v={self.settings.speed},t=0,r=0)\n'
        try:
            self.command_socket.sendall(command.encode('ascii'))
            deadline = time.monotonic() + self.settings.motion_timeout
            while True:
                self.check_stop()
                if time.monotonic() >= deadline:
                    raise TimeoutError('robot did not reach the requested pose')
                actual = self.pose()
                if np.all(np.abs(actual[:3] - target[:3]) < .001) and rotation_error(actual[3:], target[3:]) < .05:
                    return
                self.stop_event.wait(.01)
        except BaseException:
            # Stop from the worker itself; a blocked UI/inference loop must not
            # delay this request. Preserve the actual motion error if stop fails.
            with suppress(OSError):
                self.command_socket.sendall(b'stopl(1.0)\n')
            raise

    def close(self):
        if self.command_socket is not None:
            try:
                self.command_socket.sendall(b'stopl(1.0)\n')
            finally:
                self.command_socket.close()
                self.command_socket = None


class Sorter:
    def __init__(self, arm, vacuum, stop_event):
        self.arm = arm
        self.vacuum = vacuum
        self.stop_event = stop_event

    def check_stop(self):
        if self.stop_event.is_set():
            raise StopRequested('monitor requested a stop')

    def home(self):
        self.check_stop()
        self.arm.move(HOME)
        self.check_stop()
        self.vacuum.off()

    def sort(self, targets):
        """Pick one supported component, then return home for a fresh image."""
        self.check_stop()
        candidates = [row for row in targets if row[0] in HIGH_VALUE_CLASSES | LOW_VALUE_CLASSES]
        if not candidates:
            return
        row = detections_to_poses(candidates[:1], self.arm.pose())[0]
        pickup = row[1:].copy()
        drop = np.array(HIGH_BIN if row[0] in HIGH_VALUE_CLASSES else LOW_BIN, dtype=float)
        pickup[2] = .15
        self.arm.move(pickup)
        self.check_stop()
        self.vacuum.on()
        pickup[2] = -.005
        self.arm.move(pickup)
        pickup[2] = .15
        self.arm.move(pickup)
        drop[2] = .2
        self.arm.move(drop)
        drop[2] = .1
        self.arm.move(drop)
        self.check_stop()
        self.vacuum.off()
        drop[2] = .2
        self.arm.move(drop)
        self.home()

    def close(self):
        try:
            self.arm.close()
        finally:
            self.vacuum.close()
