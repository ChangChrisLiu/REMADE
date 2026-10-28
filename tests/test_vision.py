import unittest
from types import SimpleNamespace
import numpy as np

from remade.vision import Detector, RealSenseStream


class Tensor:
    def __init__(self, data):
        self.data = np.asarray(data)
    def cpu(self):
        return self
    def numpy(self):
        return self.data


class VisionTests(unittest.TestCase):
    def test_detector_reuses_model_and_returns_pixel_centers(self):
        calls = []
        class Model:
            def predict(self, frame, **kwargs):
                calls.append(kwargs)
                return [SimpleNamespace(
                    boxes=SimpleNamespace(xywh=Tensor([[320, 180, 40, 20]]),
                                          cls=Tensor([2]), conf=Tensor([0.95])),
                    plot=lambda **kwargs: frame)]
        model = Model()
        detector = Detector(model=model)
        frame = np.zeros((360, 640, 3), dtype=np.uint8)
        first, second = detector(frame), detector(frame)
        np.testing.assert_array_equal(first.targets, [[2, 320, 180]])
        np.testing.assert_array_equal(second.targets, first.targets)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]['conf'], 0.9)

    def test_empty_detections_have_consistent_shape(self):
        result = SimpleNamespace(boxes=None, plot=lambda **kwargs: 'image')
        detector = Detector(model=SimpleNamespace(predict=lambda *a, **k: [result]))
        self.assertEqual(detector('input').targets.shape, (0, 3))

    def test_sorting_model_must_match_the_expected_class_ids(self):
        model = SimpleNamespace(names={0: 'unrelated object'})
        with self.assertRaisesRegex(ValueError, 'class'):
            Detector(model=model, expected_names={0: 'Case'})

    def test_camera_starts_once_and_stops_after_multiple_frames(self):
        events = []
        data = np.zeros((2, 3, 3), dtype=np.uint8)
        class Pipeline:
            def start(self, config):
                events.append('start')
            def wait_for_frames(self, timeout):
                return SimpleNamespace(get_color_frame=lambda: SimpleNamespace(get_data=lambda: data))
            def poll_for_frames(self):
                return None
            def stop(self):
                events.append('stop')
        rs = SimpleNamespace(pipeline=Pipeline, config=lambda: SimpleNamespace(enable_stream=lambda *a: None),
                             stream=SimpleNamespace(color='color'), format=SimpleNamespace(bgr8='bgr8'))
        camera = RealSenseStream(rs_module=rs)
        first = camera.read()
        camera.read()
        camera.close()
        camera.close()
        self.assertEqual(events, ['start', 'stop'])
        self.assertFalse(np.shares_memory(first, data))


if __name__ == '__main__':
    unittest.main()
