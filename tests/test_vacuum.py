import unittest
from remade.config import Settings
from remade.vacuum import VacuumController


class Client:
    def __init__(self, **kwargs):
        self.writes = []
        self.closed = False
    def connect(self):
        return True
    def write_registers(self, **kwargs):
        self.writes.append(kwargs)
        return type('Response', (), {'isError': lambda self: False})()
    def close(self):
        self.closed = True


class VacuumTests(unittest.TestCase):
    def test_pressure_and_release_commands_use_both_channels(self):
        client = Client()
        vacuum = VacuumController(Settings(vacuum_percent=60), serial_device='test-device',
                                  client_factory=lambda **kwargs: client)
        vacuum.on()
        vacuum.off()
        vacuum.close()
        self.assertEqual(client.writes, [
            {'address': 0, 'values': [316, 316], 'unit': 65},
            {'address': 0, 'values': [0, 0], 'unit': 65}])
        self.assertTrue(client.closed)

    def test_failed_modbus_write_is_not_treated_as_success(self):
        client = Client()
        client.write_registers = lambda **kwargs: type('Response', (), {'isError': lambda self: True})()
        vacuum = VacuumController(Settings(), serial_device='test-device', client_factory=lambda **kwargs: client)
        try:
            with self.assertRaises(ConnectionError):
                vacuum.on()
        finally:
            vacuum.close()

    def test_invalid_pressure_is_rejected_before_device_access(self):
        with self.assertRaises(ValueError):
            Settings(vacuum_percent=255)
