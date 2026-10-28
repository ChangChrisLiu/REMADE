"""Command-line composition; device dependencies are loaded only when needed."""

import argparse
from contextlib import ExitStack
from pathlib import Path
import sys
from threading import Event
from .config import CLASS_NAMES, MODEL_PATH, Settings
from .monitor import run_monitor
from .robot import Sorter, URSocket
from .vacuum import VacuumController
from .vision import Detector, OpenCVDisplay, RealSenseStream


def parser():
    result = argparse.ArgumentParser(description='REMADE live phone-component monitoring and optional robot sorting')
    result.add_argument('--sort', action='store_true', help='connect to the robot and sort one component per fresh observation')
    result.add_argument('--weights', type=Path, default=MODEL_PATH, help='YOLO checkpoint path')
    result.add_argument('--confidence', type=float, default=.9, help='detection confidence threshold (default: 0.9)')
    result.add_argument('--fps', type=int, default=30, help='requested camera capture FPS; resolution stays calibrated at 1920x1080')
    result.add_argument('--robot-ip', default=Settings.host, help='UR controller host')
    result.add_argument('--speed', type=float, default=Settings.speed, help='Cartesian speed in metres/second')
    result.add_argument('--acceleration', type=float, default=Settings.acceleration, help='Cartesian acceleration in metres/second squared')
    result.add_argument('--vacuum-percent', type=int, default=Settings.vacuum_percent, help='vacuum setpoint, 1 to 80 (default: 60)')
    result.add_argument('--serial-device', help='existing vacuum serial device; otherwise start an owned socat bridge')
    return result


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    if not args.weights.is_file():
        cli.error(f'Model file not found: {args.weights}')
    if not 0 < args.confidence < 1 or args.fps <= 0:
        cli.error('confidence must be between 0 and 1, and FPS must be positive')
    try:
        settings = Settings(host=args.robot_ip, speed=args.speed, acceleration=args.acceleration,
                            vacuum_percent=args.vacuum_percent)
        stop = Event()
        # Startup failures close every resource already opened. The monitor
        # takes lifecycle ownership only once all setup has succeeded.
        with ExitStack() as setup:
            detector = Detector(args.weights, args.confidence, expected_names=CLASS_NAMES if args.sort else None)
            display = OpenCVDisplay()
            setup.callback(display.close)
            camera = RealSenseStream(fps=args.fps)
            setup.callback(camera.close)
            robot = None
            if args.sort:
                # Verify capture, inference and display before any motion. This
                # observation is discarded; selection happens after homing.
                preview = detector(camera.read())
                if not display.show(preview.frame, 'CHECKING'):
                    return 0
                robot = Sorter(URSocket(settings, stop), VacuumController(settings, args.serial_device), stop)
                setup.callback(robot.close)
            setup.pop_all()
        print('REMADE: ' + ('live monitoring + sorting' if args.sort else 'live monitoring'))
        run_monitor(camera, detector, display, robot, stop)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f'REMADE: {exc}', file=sys.stderr)
        return 1
    return 0
