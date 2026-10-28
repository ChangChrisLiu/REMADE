"""Pure coordinate transforms; no device access or optional vision imports."""

import numpy as np
from .config import BASE_CALIBRATION, CAMERA_MATRIX, PICK_ROTATION, TCP_CAMERA


def rotation_matrix(vector):
    vector = np.asarray(vector, dtype=float)
    if vector.shape != (3,) or not np.isfinite(vector).all():
        raise ValueError('rotation vector must contain three finite radians')
    theta = np.linalg.norm(vector)
    if theta < 1e-12:
        return np.eye(3)
    x, y, z = vector / theta
    cross = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    return np.eye(3) + np.sin(theta) * cross + (1 - np.cos(theta)) * (cross @ cross)


def rotation_error(actual, target):
    relative = rotation_matrix(actual).T @ rotation_matrix(target)
    return float(np.arccos(np.clip((np.trace(relative) - 1) / 2, -1, 1)))


def project_pixel_to_plane(pixel, rotation, translation, intrinsics, height=0):
    rotation = np.asarray(rotation, dtype=float)
    ray = np.linalg.solve(rotation, np.linalg.solve(intrinsics, [*pixel, 1.0]))
    offset = np.linalg.solve(rotation, np.asarray(translation).reshape(3))
    if abs(ray[2]) < 1e-12:
        raise ValueError('camera ray is parallel to the calibration plane')
    scale = (height + offset[2]) / ray[2]
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('calibration plane is not in front of the camera')
    point = ray * scale - offset
    if not np.isfinite(point).all():
        raise ValueError('non-finite projected point')
    return point


def detections_to_poses(detections, tcp):
    detections = np.asarray(detections, dtype=float).reshape(-1, 3)
    tcp = np.asarray(tcp, dtype=float)
    if tcp.shape != (6,) or not np.isfinite(tcp).all() or not np.isfinite(detections).all():
        raise ValueError('detections and TCP pose must be finite')
    base_tcp = np.eye(4)
    base_tcp[:3, :3] = rotation_matrix(tcp[3:])
    base_tcp[:3, 3] = tcp[:3] * 1000
    base_calibration = np.asarray(BASE_CALIBRATION)
    camera_calibration = np.linalg.inv(TCP_CAMERA) @ np.linalg.inv(base_tcp) @ base_calibration
    poses = []
    for class_id, u, v in detections:
        point = project_pixel_to_plane([u, v], camera_calibration[:3, :3],
                                      camera_calibration[:3, 3], CAMERA_MATRIX)
        base = base_calibration @ np.append(point, 1)
        poses.append([class_id, base[0] / 1000, base[1] / 1000, 0, *PICK_ROTATION])
    return np.asarray(poses, dtype=float).reshape(-1, 7)
