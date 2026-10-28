import subprocess
import time
# import rclpy
# from rclpy.node import Node
# import urx
# from std_srvs.srv import Trigger
import collections
collections.Iterable = collections.abc.Iterable
from onrobot import VG
import cv2
import numpy as np
from ultralytics import YOLO
from cameratest import RealsenseD435
import socket
import struct
import util
import rtde
import torch
import matplotlib.pyplot as plt


Camera_Instinct = np.array([
    [1354.73552660491, 0, 970.580407580363],
    [0, 1360.53566517000, 542.269475710679],
    [0, 0, 1]])



def ObjectDetection(img):
    model = YOLO('smallmodeldet.pt')
    results = model(img)
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        # masks = result.masks 
    print(result.boxes)
    position_tensor = result.boxes.xywhn
    position_tensor = position_tensor.to(torch.float64)
    position_np = position_tensor.cpu().numpy()
    classes_tensor = result.boxes.cls
    classes_tensor = classes_tensor.to(torch.float64)
    classes_np = classes_tensor.cpu().numpy()
    confid_tensor = result.boxes.conf
    confid_tensor = confid_tensor.to(torch.float64)
    confid_np = confid_tensor.cpu().numpy()
    high_confid_np = np.where(confid_np>0.9)
    position_np = position_np[high_confid_np]
    classes_np = classes_np [high_confid_np]
    # print(position_np)
    # print(classes_np)
    # np.set_printoptions(precision=6, floatmode='fixed')
    # 只提取 position_np 的前两个数据
    position_first = 1920 * position_np[:, 0]
    position_first = position_first.reshape(-1,1)
    print(position_first)

    position_second = 1080 * position_np[:, 1]
    position_second = position_second.reshape(-1,1)
    print(position_second)
    position_first_two = np.hstack((position_first,position_second))

# 将 classes_np 重塑为列向量，以便与 position_first_two 进行合并
    classes_np_column = classes_np.reshape(-1, 1)

# 将 classes_np 与 position_first_two 水平合并
    result_matrix = np.hstack((classes_np_column, position_first_two))
    # np.set_printoptions(suppress=True, precision=6, floatmode='fixed')
    print(result_matrix)
    return result_matrix


img = '/home/grads/c/changliu.chris/REMADE/REMADE/001.png'
ObjectDetection(img)
