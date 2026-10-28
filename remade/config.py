"""Lab-specific calibration from the original REMADEDEMO.py.

Translations in the calibration matrices are millimetres. Robot poses are
metres plus an axis-angle rotation vector in radians. Recalibrate after any
camera, tool, fixture or robot-base change.
"""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / 'assets' / 'models' / 'smallmodeldet.pt'
CLASS_NAMES = {0: 'Case', 1: 'Film', 2: 'High Value Middle', 3: 'Screen', 4: 'iPhone Case'}
LOW_VALUE_CLASSES = frozenset({0, 1, 3})
HIGH_VALUE_CLASSES = frozenset({2, 4})

HOME = (0.47235829, -0.3052461, 0.46904554, 2.2142888, -2.21759341, 0.09359272)
HIGH_BIN = (-0.33768291, -0.61855289, 0.1531814, -0.85744133, 3.01975499, -0.11043932)
LOW_BIN = (-0.37072683, -0.29942229, 0.1512853, 0.07627575, -3.11429522, 0.13188759)
PICK_ROTATION = (2.18204119, -2.20759957, 0.06040668)
CAMERA_MATRIX = ((1354.73552660491, 0, 970.580407580363),
                 (0, 1360.53566517000, 542.269475710679), (0, 0, 1))
TCP_CAMERA = ((0.0573716354110889, -0.941544728553317, -0.0588982747648019, 128.761243472197),
              (0.993587593396270, -0.0241725382880964, 0.0369118855642246, -43.5733431156015),
              (-0.0218399530097034, 0.00604283245196839, 0.997682646759965, -67.7384000828499),
              (0, 0, 0, 1))
BASE_CALIBRATION = ((-0.991372360069160, 0.0344899310385318, 0.00167292845223808, 579.046363776787),
                    (-0.0497666569959037, 0.901805219997417, -0.00111212489025246, -485.104685940117),
                    (-0.000888232419437007, -0.0289641764006589, -0.958527707367941, -7.41394645813782),
                    (0, 0, 0, 1))


@dataclass(frozen=True)
class Settings:
    host: str = '10.125.145.89'
    port: int = 30003
    vacuum_port: int = 54321
    socket_timeout: float = 3.0
    motion_timeout: float = 30.0
    speed: float = 0.2
    acceleration: float = 0.5
    vacuum_percent: int = 60

    def __post_init__(self):
        if not self.host or any(c in self.host for c in ',/ \t\r\n'):
            raise ValueError('host must be a plain hostname or IPv4 address')
        if not (0 < self.port < 65536 and 0 < self.vacuum_port < 65536):
            raise ValueError('ports must be between 1 and 65535')
        import math
        for value in (self.socket_timeout, self.motion_timeout, self.speed, self.acceleration):
            if not math.isfinite(value) or value <= 0:
                raise ValueError('timeouts, speed and acceleration must be positive and finite')
        if not 1 <= self.vacuum_percent <= 80:
            raise ValueError('vacuum_percent must be between 1 and 80')
