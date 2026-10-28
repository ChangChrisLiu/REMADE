import unittest
import numpy as np
from remade.geometry import rotation_matrix, project_pixel_to_plane, rotation_error


class GeometryTests(unittest.TestCase):
    def test_zero_rotation_is_identity(self):
        np.testing.assert_allclose(rotation_matrix([0, 0, 0]), np.eye(3), atol=1e-12)

    def test_equivalent_pi_rotations_have_zero_distance(self):
        self.assertAlmostEqual(rotation_error([0, 0, np.pi], [0, 0, -np.pi]), 0)

    def test_known_pixel_intersects_known_plane(self):
        # Camera at z=-10, identity rotation, K=identity. Ray (2,3,1)
        # reaches plane z=0 at world point (20,30,0).
        point = project_pixel_to_plane([2, 3], np.eye(3), [0, 0, 10], np.eye(3), 0)
        np.testing.assert_allclose(point, [20, 30, 0])

    def test_parallel_ray_is_rejected(self):
        rotation = rotation_matrix([0, np.pi / 2, 0])
        with self.assertRaises(ValueError):
            project_pixel_to_plane([0, 0], rotation, [0, 0, 10], np.eye(3), 0)
