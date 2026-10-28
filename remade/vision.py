"""Persistent RealSense stream, one YOLO instance, and an OpenCV preview."""

from dataclasses import dataclass
import time
import numpy as np


@dataclass
class DetectionFrame:
    frame: np.ndarray
    targets: np.ndarray  # rows: class ID, center x (pixels), center y (pixels)


class RealSenseStream:
    def __init__(self, width=1920, height=1080, fps=30, rs_module=None):
        if rs_module is None:
            import pyrealsense2 as rs_module
        self.pipeline = rs_module.pipeline()
        self.closed = True
        config = rs_module.config()
        config.enable_stream(rs_module.stream.color, width, height, rs_module.format.bgr8, fps)
        self.pipeline.start(config)
        self.closed = False

    def read(self):
        color = self.pipeline.wait_for_frames(2000).get_color_frame()
        if not color:
            raise RuntimeError('RealSense did not provide a color frame')
        return np.asanyarray(color.get_data()).copy()

    def discard_pending(self):
        while self.pipeline.poll_for_frames():
            pass

    def close(self):
        if not self.closed:
            self.closed = True
            self.pipeline.stop()


class Detector:
    def __init__(self, weights=None, confidence=0.9, model=None, expected_names=None):
        if not 0 < confidence < 1:
            raise ValueError('confidence must be between 0 and 1')
        if model is None:
            from ultralytics import YOLO
            model = YOLO(str(weights))
        self.model = model
        self.confidence = confidence
        if expected_names is not None and self.model.names != expected_names:
            raise ValueError('model class IDs/names do not match the configured sorting classes')

    def __call__(self, frame):
        result = self.model.predict(frame, conf=self.confidence, verbose=False)[0]
        targets = np.empty((0, 3), dtype=float)
        if result.boxes is not None:
            boxes = result.boxes
            centers = boxes.xywh.cpu().numpy()[:, :2]
            classes = boxes.cls.cpu().numpy()
            confidence = boxes.conf.cpu().numpy()
            keep = confidence >= self.confidence
            targets = np.column_stack((classes[keep], centers[keep]))
        return DetectionFrame(result.plot(masks=False), targets)


class OpenCVDisplay:
    def __init__(self):
        import cv2
        self.cv2 = cv2
        self.name = 'REMADE | Live monitoring'
        self.last_frame = time.monotonic()
        cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.name, 1280, 720)

    def show(self, frame, status):
        now = time.monotonic()
        fps = 1 / max(now - self.last_frame, 1e-6)
        self.last_frame = now
        self.cv2.putText(frame, f'{status} | {fps:.1f} FPS | Q / Esc: quit',
                         (20, 40), self.cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        self.cv2.imshow(self.name, frame)
        key = self.cv2.waitKey(1) & 0xff
        return key not in (ord('q'), ord('Q'), 27) and self.cv2.getWindowProperty(
            self.name, self.cv2.WND_PROP_VISIBLE) >= 1

    def close(self):
        self.cv2.destroyAllWindows()
