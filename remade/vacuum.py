"""OnRobot two-channel Modbus control with an owned serial bridge.

Register addresses and serial settings follow the archived onrobot.py.
A successful write is a command acknowledgement, not proof of a held part.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


class VacuumController:
    def __init__(self, settings, serial_device=None, client_factory=None):
        self.settings = settings
        self.serial_device = serial_device
        self.client_factory = client_factory
        self.client = None
        self.bridge = None
        self.directory = None

    def _connect(self):
        if self.client is not None:
            return
        if self.client_factory is None:
            from pymodbus.client.sync import ModbusSerialClient
            self.client_factory = ModbusSerialClient
        try:
            device = self.serial_device
            if device is None:
                if os.name != 'posix' or shutil.which('socat') is None:
                    raise RuntimeError('Automatic vacuum bridge requires Linux and socat; otherwise pass --serial-device')
                self.directory = tempfile.TemporaryDirectory(prefix='remade-vacuum-')
                device = str(Path(self.directory.name) / 'ttyUR')
                self.bridge = subprocess.Popen(
                    ['socat', f'pty,link={device},raw,ignoreeof,waitslave',
                     f'tcp:{self.settings.host}:{self.settings.vacuum_port}'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                deadline = time.monotonic() + self.settings.socket_timeout
                while not Path(device).exists():
                    if self.bridge.poll() is not None:
                        raise ConnectionError('socat vacuum bridge exited during startup')
                    if time.monotonic() >= deadline:
                        raise TimeoutError('vacuum serial bridge did not become ready')
                    time.sleep(.01)
            self.client = self.client_factory(method='rtu', port=device, stopbits=1,
                                               bytesize=8, parity='E', baudrate=115200,
                                               timeout=1, retries=0)
            if not self.client.connect():
                raise ConnectionError('could not open the vacuum serial device')
        except BaseException:
            self.close()
            raise

    def prepare(self):
        """Check the controller with a read only; preserve any held part."""
        self._connect()
        response = self.client.read_holding_registers(address=2, count=1, unit=65)
        if response is None or response.isError():
            raise ConnectionError('vacuum controller did not answer the startup register read')
        registers = getattr(response, 'registers', None)
        if not isinstance(registers, (list, tuple)) or len(registers) != 1 or \
                not isinstance(registers[0], int) or not 0 <= registers[0] <= 65535:
            raise ConnectionError('vacuum controller returned an invalid startup register response')

    def _write(self, value):
        self._connect()
        response = self.client.write_registers(address=0, values=[value, value], unit=65)
        if response is None or response.isError():
            raise ConnectionError('vacuum controller rejected the Modbus command')

    def on(self):
        self._write(0x0100 + self.settings.vacuum_percent)

    def off(self):
        self._write(0)

    def close(self):
        try:
            if self.client is not None:
                self.client.close()
                self.client = None
        finally:
            try:
                if self.bridge is not None:
                    if self.bridge.poll() is None:
                        self.bridge.terminate()
                        try:
                            self.bridge.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            self.bridge.kill()
                            self.bridge.wait(timeout=2)
                    self.bridge = None
            finally:
                if self.directory is not None:
                    self.directory.cleanup()
                    self.directory = None
