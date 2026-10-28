"""Keep image acquisition responsive while one robot job runs at a time."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Event


class StopRequested(Exception):
    """Cooperative cancellation of an in-progress robot operation."""


def run_monitor(camera, detector, display, robot=None, stop_event=None):
    """Own and close camera/display/robot; never queue stale detection batches.

    Camera: read(), discard_pending(), close(). Detector(frame) returns an
    object with frame and targets. Display.show(frame, status) returns False
    on exit. Robot.home()/sort(targets) run only on the single worker thread.
    """
    stop = stop_event if stop_event is not None else Event()
    executor = ThreadPoolExecutor(max_workers=1) if robot is not None else None
    future = None
    failure = None
    try:
        if robot is not None:
            future = executor.submit(robot.home)
        while not stop.is_set():
            if future is not None and future.done():
                future.result()
                future = None
                camera.discard_pending()
            # Read only after the previous job is observed complete. A job that
            # finishes during inference cannot make this frame eligible.
            ready = robot is not None and future is None
            result = detector(camera.read())
            status = 'MONITOR' if robot is None else ('READY' if ready else 'SORTING')
            if not display.show(result.frame, status):
                break
            if ready and len(result.targets):
                future = executor.submit(robot.sort, deepcopy(result.targets))
    except BaseException as exc:
        failure = exc
    finally:
        stop.set()
        if executor is not None:
            # Defer repeated Ctrl+C until the cooperative worker has exited;
            # resources must not be closed underneath a running robot task.
            while True:
                try:
                    executor.shutdown(wait=True)
                    if future is not None:
                        future.result()
                    break
                except KeyboardInterrupt as exc:
                    if failure is None:
                        failure = exc
                    # A worker can itself finish with KeyboardInterrupt. Its
                    # completed future will raise it forever, so do not retry.
                    if future is not None and future.done():
                        break
                except BaseException as exc:
                    if not isinstance(exc, StopRequested) and failure is None:
                        failure = exc
                    break
        for resource in (robot, camera, display):
            if resource is not None:
                try:
                    resource.close()
                except BaseException as exc:
                    if failure is None:
                        failure = exc
    if failure is not None:
        raise failure
