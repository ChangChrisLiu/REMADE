import rtde_control
import rtde_receive
import time
import numpy as np
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
import pickle



Test1_TCP = np.array([0.57990133, -0.44711561,  0.27736907,  2.1980858, -2.23729211,  0.06219291])
Test1_Joint = np.array([2.30167532, -0.94790252,  1.29957039,  4.32131927, -1.5745104,   5.46153021])

Test2_TCP = np.array([0.5813679,  -0.45336767,  0.21744955,  2.19517291, -2.24142601,  0.05465037])
Test2_Joint = np.array([2.29786849, -1.01231529,  1.10524971,  4.58497254, -1.57399446, 5.4610548])

Test3_TCP = np.array([0.6355005031084251, -0.4533619749476544, 0.29307245901577356, 2.1951705651266744, -2.241447894692341, 0.054552057427810705])
Test3_Joint = np.array([2.3512940406799316, -0.8668060463717957, 0.67267352739443, 4.872234332352438, -1.5761807600604456, 5.514803409576416])

Test4_TCP = np.array([0.5391411911100089, -0.4533584469524271, 0.32742772773754153, 2.195193697659474, -2.2413990294940027, 0.05462059097943739])
Test4_Joint = np.array([2.251925230026245, -1.0965730410865326, 0.9536693731891077, 4.820721569448271, -1.5724056402789515, 5.415256977081299])


print(Test4_Joint)


rtde_c = rtde_control.RTDEControlInterface("10.125.145.89")
rtde_r = rtde_receive.RTDEReceiveInterface("10.125.145.89")
init_q = rtde_r.getActualQ()



def load_path_high_go():
    '''
    loads the MPNet planned path
    '''

    file_name = "paths_for_demo/start_to_high.pkl"
    with open(file_name, 'rb') as f:
        path = pickle.load(f)
    
    return path

def load_path_low_go():
    '''
    loads the MPNet planned path
    '''

    file_name = "paths_for_demo/start_to_low.pkl"
    with open(file_name, 'rb') as f:
        path = pickle.load(f)
    
    return path

def load_path_high_back():
    '''
    loads the MPNet planned path
    '''

    file_name = "paths_for_demo/high_to_home.pkl"
    with open(file_name, 'rb') as f:
        path = pickle.load(f)
    
    return path

def load_path_low_back():
    '''
    loads the MPNet planned path
    '''

    file_name = "paths_for_demo/low_to_home.pkl"
    with open(file_name, 'rb') as f:
        path = pickle.load(f)
    
    return path


# rtde_c.moveJ(Test1_Joint)
# rtde_c.moveJ(Test2_Joint)
# rtde_c.moveJ(Test3_Joint)
# rtde_c.moveJ(Test4_Joint)



velocity = 1.4
acceleration = 1.05
blend_1 = 0.02
blend_2 = 0.02
blend_3 = 0.02



# joint_velocity = Joint_Speed
# joint_acceleration = Joint_Accele
# blend = 0.02
# for row in path:
#     row.extend([joint_velocity, joint_acceleration, blend])

# path_pose1 = [Test1_Joint.tolist(), velocity, acceleration, blend_1]
# path_pose2 = [Test2_Joint.tolist(), velocity, acceleration, blend_2]
# path_pose3 = [Test3_Joint.tolist(), velocity, acceleration, blend_3]
# path = [path_pose1, path_pose2, path_pose3]

# print(path_pose1)

# # Send a linear path with blending in between - (currently uses separate script)
# rtde_c.moveJ(path)

path1 = load_path_high_go()
print(path1[0])
p1 = [*path1[0],velocity, acceleration, blend_1]
print(p1)

for row in path1:
    row.extend([acceleration, velocity, blend_1])


print(path1)

path_pose1 = Test1_Joint.tolist() + [velocity, acceleration, blend_1]
path_pose2 = Test2_Joint.tolist() + [velocity, acceleration, blend_2]
path_pose3 = Test3_Joint.tolist() + [velocity, acceleration, blend_3]
path = [path_pose1, path_pose2, path_pose3]
print(path)

# # 发送带有混合的路径
# rtde_c.moveJ(path, asynchronous=False)


# Parameters
# velocity = 0.5
# acceleration = 0.5
# dt = 1.0/500  # 2ms
# lookahead_time = 0.1
# gain = 100
# joint_q = [-1.54, -1.83, -2.28, -0.59, 1.60, 0.023]

# def move_to_joint(target_joint):
#     velocity = 0.2
#     acceleration = 0.05
#     dt = 1.0/500  # 2ms
#     lookahead_time = 0.1
#     gain = 100
#     joint_tolerance = [0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
#     rtde_c.servoJ(target_joint, velocity, acceleration, dt, lookahead_time, gain)
#         # Block until robot reaches home state
#     actual_joint_positions = rtde_r.getActualQ()
#     while not (np.all([np.abs(actual_joint_positions[j] - target_joint[j]) < joint_tolerance for j in range(6)])):
#         actual_joint_positions = rtde_r.getActualQ()
#     time.sleep(0.01)


# move_to_joint(Joint_Position_1)
# move_to_joint(Joint_Position_2)
# move_to_joint(Joint_Position_3)
# move_to_joint(Joint_Position_4)

# rtde_c.servoJ(Joint_Position_1, velocity, acceleration, dt, lookahead_time, gain)


# Move to initial joint position with a regular moveJ
# rtde_c.moveJ(joint_q)

# # Execute 500Hz control loop for 2 seconds, each cycle is 2ms
# for i in range(1000):
#     t_start = rtde_c.initPeriod()
#     rtde_c.servoJ(joint_q, velocity, acceleration, dt, lookahead_time, gain)
#     joint_q[0] += 0.001
#     joint_q[1] += 0.001
#     rtde_c.waitPeriod(t_start)

# rtde_c.servoStop()
# rtde_c.stopScript()



















# acceleration = 0.5
# dt = 1.0/500  # 2ms
# joint_speed = [0.005, 0.005, 0.0, 0.0, 0.0, 0.0]
# rtde_c.speedJ(joint_speed, acceleration, dt)
# time.sleep(5)
# rtde_c.speedStop()

# Move to initial joint position with a regular moveJ
# rtde_c.moveJ(Joint_Position_1)
# rtde_c.moveJ(Joint_Position_2)
# rtde_c.moveJ(Joint_Position_3)
# rtde_c.moveJ(Joint_Position_4)
# rtde_c.moveJ(Joint_Position_5)

# Execute 500Hz control loop for 2 seconds, each cycle is 2ms
# for i in range(1000):
#     t_start = rtde_c.initPeriod()
#     rtde_c.speedJ(joint_speed, acceleration, dt)
#     # joint_speed[0] += 0.0005
#     # joint_speed[1] += 0.0005
#     rtde_c.waitPeriod(t_start)

# rtde_c.speedStop()
# rtde_c.stopScript()

# print(actual_q)

