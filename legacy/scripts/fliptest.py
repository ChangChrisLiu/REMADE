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


HOST = "10.125.145.89"

PORT = 30003
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect((HOST, PORT))



HomePosition = np.array([0.47235829, -0.3052461,   0.46904554,  2.2142888,  -2.21759341,  0.09359272])
HighValue_Position = np.array([-0.33768291, -0.61855289,  0.1531814, -0.85744133,  3.01975499, -0.11043932])
LowValue_Position = np.array([-0.37072683, -0.29942229,  0.1512853,  0.07627575, -3.11429522,  0.13188759])

Initial_Test_Position_TCP = np.array([ 0.54447048, -0.44275058,  0.00226764, -2.2142351,   2.20327653, -0.14198995])
Initial_Test_Position_joint= np.array([-0.4867633,  -2.20796456, -1.58886814, -0.82474221,  1.55712175, -0.49313337])

Initial_Test_Position_Upper_TCP = np.array([ 0.54447048, -0.44275058,  0.1526764, -2.2142351,   2.20327653, -0.14198995])


Case_flip_insert_Position_Ready_TCP = np.array([-1.20692529e-03, -6.55855966e-01,  2.85924404e-01,  3.41598485e-02,-1.55315815e+00,  5.32026888e-02])
Case_flip_insert_Position_Ready_joint= np.array([-0.97727472, -2.36162295, -0.98766476, -2.97074713,  0.53784806, 1.61460614])

Case_flip_insert_Position_Release_TCP = np.array([-1.22410589e-03, -6.55861469e-01,  1.81025772e-01,  3.41278164e-02, -1.55316159e+00,  5.32148233e-02])
Case_flip_insert_Position_Release_Joint = np.array([-0.97719509, -2.44892611, -1.10784805, -2.763168,    0.53759652,  1.61457884])

Case_flip_insert_Position_Free_TCP = np.array([0.06763018, -0.65586492,  0.18103209,  0.03411908, -1.55318073,  0.05326839])
Case_flip_insert_Position_Free_Joint = np.array([-0.89751751, -2.52432646, -0.96258867, -2.82861294,  0.61713874,  1.60934103])

Case_flip_insert_Position_Rotation_way1_TCP = np.array([-0.01649786, -0.6558774,   0.38497674, -0.01697917, -3.08049794,  0.0863543 ])
Case_flip_insert_Position_Rotation_way1_Joint = np.array([-1.36182815, -1.89849009, -1.35078657, -1.4215727,   1.49915743,  0.21873569])

Case_flip_pickup_Position_Ready_TCP = np.array([-0.05180437, -0.65586058,  0.13879065,  0.05282193,  1.65285575, -0.03633536])
Case_flip_pickup_Position_Ready_Joint= np.array([-1.85171491, -2.41834988, -1.18390858, -2.32417121,  2.90095925, -1.21518547])

Case_flip_pickup_Position_Grab_TCP = np.array([-0.01905557, -0.65586943,  0.13879065,  0.05276021,  1.65287313, -0.03641582])
Case_flip_pickup_Position_Grab_Joint= np.array([-1.80641729, -2.39233985, -1.28540993, -2.17029156,  2.94268894, -1.13497526])

Case_flip_pickup_Position_Out_TCP = np.array([-0.01905557, -0.65585813,  0.35003914,  0.05280975,  1.65286439, -0.03633426])
Case_flip_pickup_Position_Out_Joint = np.array([-1.7891801,  -2.19968667, -1.05763638, -2.5498835,   2.9587338,  -1.09335024])




Camera_Instinct = np.array([
    [1354.73552660491, 0, 970.580407580363],
    [0, 1360.53566517000, 542.269475710679],
    [0, 0, 1]])


# Camera_Instinct = np.array([
#     [1353.37961859407, 0, 958.022554],
#     [0, 1354.49471811200, 542.099984],
#     [0, 0, 1]])


# Camera_Instinct = np.array([
#     [948.443, 0, 964.574],
#     [0, 948.443, 528.128],
#     [0, 0, 1]])





def get_current_tcp():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    data = tcp_socket.recv(1108)
    position = struct.unpack('!6d', data[444:492])
    # tcp_socket.close()
    return np.asarray(position)


def move_to_tcp(target_tcp):
    tool_acc = 1.2 # Safe: 0.5
    tool_vel = 0.8  # Safe: 0.2
    tool_pos_tolerance = [0.001, 0.001, 0.001, 0.05, 0.05, 0.05]
    tcp_command = "movel(p[%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=0,r=0)\n" % (
        target_tcp[0], target_tcp[1], target_tcp[2], target_tcp[3], target_tcp[4],
        target_tcp[5],
        tool_acc, tool_vel)
    # tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.connect((HOST, PORT))
    tcp_socket.send(str.encode(tcp_command))  # 利用字符串的encode方法编码成bytes，默认为utf-8类型
    # tcp_socket.close()
    # 确保已达到目标点，就可以紧接着发送下一条指令
    actual_pos = get_current_tcp()
    target_rpy = util.rv2rpy(target_tcp[3], target_tcp[4], target_tcp[5])
    rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
    while not (all([np.abs(actual_pos[j] - target_tcp[j]) < tool_pos_tolerance[j] for j in range(3)])
               and all([np.abs(rpy[j] - target_rpy[j]) < tool_pos_tolerance[j+3] for j in range(3)])):
        actual_pos = get_current_tcp()
        rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
        time.sleep(0.01)



def get_current_joint():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    state_data = tcp_socket.recv(1108)
    position = parse_tcp_state_data(state_data, 'joint_data')
    # print(position)
    tcp_socket.close()
    return np.asarray(position)



def parse_tcp_state_data(data, subpasckage):
        dic = {'MessageSize': 'i', 'Time': 'd', 'q target': '6d', 'qd target': '6d', 'qdd target': '6d',
               'I target': '6d',
               'M target': '6d', 'q actual': '6d', 'qd actual': '6d', 'I actual': '6d', 'I control': '6d',
               'Tool vector actual': '6d', 'TCP speed actual': '6d', 'TCP force': '6d', 'Tool vector target': '6d',
               'TCP speed target': '6d', 'Digital input bits': 'd', 'Motor temperatures': '6d', 'Controller Timer': 'd',
               'Test value': 'd', 'Robot Mode': 'd', 'Joint Modes': '6d', 'Safety Mode': 'd', 'empty1': '6d',
               'Tool Accelerometer values': '3d',
               'empty2': '6d', 'Speed scaling': 'd', 'Linear momentum norm': 'd', 'SoftwareOnly': 'd',
               'softwareOnly2': 'd',
               'V main': 'd',
               'V robot': 'd', 'I robot': 'd', 'V actual': '6d', 'Digital outputs': 'd', 'Program state': 'd',
               'Elbow position': 'd', 'Elbow velocity': '3d'}
        ii = range(len(dic))
        for key, i in zip(dic, ii):
            fmtsize = struct.calcsize(dic[key])
            data1, data = data[0:fmtsize], data[fmtsize:]
            fmt = "!" + dic[key]
            dic[key] = dic[key], struct.unpack(fmt, data1)

        if subpasckage == 'joint_data':  # get joint data
            q_actual_tuple = dic["q actual"]
            joint_data= np.array(q_actual_tuple[1])
            return joint_data
        elif subpasckage == 'cartesian_info':
            Tool_vector_actual = dic["Tool vector actual"]  # get x y z rx ry rz
            cartesian_info = np.array(Tool_vector_actual[1])
            return cartesian_info


def move_to_joint(target_joint):
    joint_acc = 1.4  # Safe: 0.5
    joint_vel = 1.05  # Safe: 0.2
    joint_tolerance = [0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    tcp_command = "movej([%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=0,r=0)\n" % (
        target_joint[0], target_joint[1], target_joint[2], target_joint[3], target_joint[4],
        target_joint[5],
        joint_acc, joint_vel)

    tcp_socket.send(str.encode(tcp_command))
        # Block until robot reaches home state
    actual_joint_positions = get_current_joint()
    while not (np.all([np.abs(actual_joint_positions[j] - target_joint[j]) < joint_tolerance for j in range(6)])):
        actual_joint_positions = get_current_joint()
    time.sleep(0.01)





def move_to_tcp_with_vacuum_on(target_tcp):
    tool_acc = 2.5 # Safe: 0.5
    tool_vel = 2.5# Safe: 0.2
    tool_pos_tolerance = [0.001, 0.001, 0.001, 0.05, 0.05, 0.05]
    # Vacuumon()
    tcp_command = "movel(p[%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=0,r=0)\n" % (
        target_tcp[0], target_tcp[1], target_tcp[2], target_tcp[3], target_tcp[4],
        target_tcp[5],
        tool_acc, tool_vel)
    # tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.connect((HOST, PORT))
    tcp_socket.send(str.encode(tcp_command))  # 利用字符串的encode方法编码成bytes，默认为utf-8类型
    # tcp_socket.close()
    # 确保已达到目标点，就可以紧接着发送下一条指令
    time.sleep(0.01)
    Vacuumon()
    actual_pos = get_current_tcp()
    target_rpy = util.rv2rpy(target_tcp[3], target_tcp[4], target_tcp[5])
    rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
    while not (all([np.abs(actual_pos[j] - target_tcp[j]) < tool_pos_tolerance[j] for j in range(3)])
               and all([np.abs(rpy[j] - target_rpy[j]) < tool_pos_tolerance[j+3] for j in range(3)])):
        actual_pos = get_current_tcp()
        rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
        time.sleep(0.01)





def move_to_tcp_with_vacuum_off(target_tcp):
    tool_acc = 2.5 # Safe: 0.5
    tool_vel = 2.5 # Safe: 0.2
    tool_pos_tolerance = [0.001, 0.001, 0.001, 0.05, 0.05, 0.05]
    # Vacuumoff()
    tcp_command = "movel(p[%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=0,r=0)\n" % (
        target_tcp[0], target_tcp[1], target_tcp[2], target_tcp[3], target_tcp[4],
        target_tcp[5],
        tool_acc, tool_vel)
    # tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.connect((HOST, PORT))
    tcp_socket.send(str.encode(tcp_command))  # 利用字符串的encode方法编码成bytes，默认为utf-8类型
    # tcp_socket.close()
    # 确保已达到目标点，就可以紧接着发送下一条指令
    time.sleep(0.01)
    Vacuumoff()
    actual_pos = get_current_tcp()
    target_rpy = util.rv2rpy(target_tcp[3], target_tcp[4], target_tcp[5])
    rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
    while not (all([np.abs(actual_pos[j] - target_tcp[j]) < tool_pos_tolerance[j] for j in range(3)])
               and all([np.abs(rpy[j] - target_rpy[j]) < tool_pos_tolerance[j+3] for j in range(3)])):
        actual_pos = get_current_tcp()
        rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
        time.sleep(0.01)


def move_to_tcp_slow(target_tcp):
    tool_acc = 0.5  # Safe: 0.5
    tool_vel = 0.15  # Safe: 0.2
    tool_pos_tolerance = [0.001, 0.001, 0.001, 0.05, 0.05, 0.05]
    tcp_command = "movel(p[%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=0,r=0)\n" % (
        target_tcp[0], target_tcp[1], target_tcp[2], target_tcp[3], target_tcp[4],
        target_tcp[5],
        tool_acc, tool_vel)
    # tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.connect((HOST, PORT))
    tcp_socket.send(str.encode(tcp_command))  # 利用字符串的encode方法编码成bytes，默认为utf-8类型
    # tcp_socket.close()
    # 确保已达到目标点，就可以紧接着发送下一条指令
    actual_pos = get_current_tcp()
    target_rpy = util.rv2rpy(target_tcp[3], target_tcp[4], target_tcp[5])
    rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
    while not (all([np.abs(actual_pos[j] - target_tcp[j]) < tool_pos_tolerance[j] for j in range(3)])
               and all([np.abs(rpy[j] - target_rpy[j]) < tool_pos_tolerance[j+3] for j in range(3)])):
        actual_pos = get_current_tcp()
        rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
        time.sleep(0.01)


def increase_move(delta_x, delta_y, delta_z, delta_theta):
    tcp = get_current_tcp()
    rpy = util.rv2rpy(tcp[3], tcp[4], tcp[5])
    rpy[2] = rpy[2] + delta_theta
    target_rv = util.rpy2rv(rpy)
    target_tcp = np.asarray([tcp[0] + delta_x, tcp[1] + delta_y, tcp[2] + delta_z,
                             target_rv[0], target_rv[1], target_rv[2]])
    move_to_tcp_slow(target_tcp)


def get_digital_output():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    data = tcp_socket.recv(1108)
    tool = struct.unpack('!d', data[1044:1052])[0]
    tcp_socket.close()
    return tool

def move_down():
    
    tcp = get_current_tcp()
    increase_move(0,0,-0.005,0)


def move_up():
    tcp = get_current_tcp()
    increase_move(0,0,0.05,0)


def grasp():
    Vacuumon()
    # Vacuumon()
    # Vacuumon()
    move_down()
    


def release():
    Vacuumoff()
    # Vacuumoff()
    # Vacuumoff()
    # move_down()
    



def go_home():
    move_to_tcp_with_vacuum_off(HomePosition)



def TCPPosetoCameraPose(TCP_Rotation_Vec, TCP_Postion):
    TCP_Camera_Trans = np.array([
    [0.0573716354110889,	-0.941544728553317,	-0.0588982747648019,	128.761243472197],
    [0.993587593396270,	-0.0241725382880964,	0.0369118855642246,	    -43.5733431156015],
    [-0.0218399530097034,	0.00604283245196839,	0.997682646759965,	-67.7384000828499],
    [0, 0, 0, 1]])


    Base_Calobration_Trans = np.array([
    [-0.991372360069160,	0.0344899310385318,	0.00167292845223808,	579.046363776787],
    [-0.0497666569959037,	0.901805219997417,	-0.00111212489025246,	-485.104685940117],
    [-0.000888232419437007,	-0.0289641764006589,	-0.958527707367941,	-7.41394645813782],
    [0, 0, 0, 1]])

    
    TCP_Rotation_Matrix = cv2.Rodrigues(TCP_Rotation_Vec)[0]
    Base_TCP_Translation = np.zeros((4, 4))
    Base_TCP_Translation[0:3, 0:3] = TCP_Rotation_Matrix
    Base_TCP_Translation[0:3, 3] = TCP_Postion
    Base_TCP_Translation[3, :] = [0, 0, 0, 1]


    TCP_Camera_Trans_Inv = np.linalg.inv(TCP_Camera_Trans)
    Base_TCP_Translation_Inv = np.linalg.inv(Base_TCP_Translation)


    Camera_Calibration_Trans = np.dot(np.dot(TCP_Camera_Trans_Inv, Base_TCP_Translation_Inv), Base_Calobration_Trans)

    Camera_Calibration_RotationMatrix = Camera_Calibration_Trans[0:3, 0:3]
    Camera_Calibration_TransVector = Camera_Calibration_Trans[0:3, 3]
    Camera_Calibration_TransVector = Camera_Calibration_TransVector .reshape(3,1)


    return Camera_Calibration_RotationMatrix, Camera_Calibration_TransVector




def single2Dto3Dpt(point2D, RotationMatrix, tVec, cameraMat, height):
    """
    Function to convert a single 2D point back to a real-world 3D point
    point2D   : A single 2D point as a list or array [u, v]
    rVec      : Rotation vector
    tVec      : Translation vector
    cameraMat : Camera Matrix used in solvePnP
    height    : Height in real-world 3D space
    Return    : A single 3D point as an array [X, Y, Z]
    """
    
    # Convert the point to a 3x1 homogeneous coordinate
    uvPoint = np.array([point2D[0], point2D[1], 1.0], dtype='float32').reshape(3, 1)
    
    # Convert rotation vector to rotation matrix
    rMat = RotationMatrix
    
    # Calculate the inverse of rotation matrix and camera matrix
    rMat_inv = np.linalg.inv(rMat)
    # print("rMat_inv")
    # print(rMat_inv)
    kMat_inv = np.linalg.inv(cameraMat)
    # print("kMat_inv")
    # print(kMat_inv)
    
    # Perform the matrix multiplications
    tempMat = np.matmul(rMat_inv, kMat_inv)
    tempMat = np.matmul(tempMat, uvPoint)
    # print("tempMat")
    # print(tempMat)
    tempMat2 = np.matmul(rMat_inv, tVec)
    # print("tempMat2")
    # print(tempMat2)
    
    # Calculate the scale factor to determine the Z coordinate
    s = (height + tempMat2[2, 0]) / tempMat[2, 0]
    
    # Calculate the 3D coordinates
    p = tempMat * s - tempMat2
    
    # Return the 3D point as a flattened array
    point3D = p.flatten()
    point3D = point3D.reshape(3,1)
    return point3D



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
    high_confid_np = np.where(confid_np>0.8)
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


def Image2TCP(img):
    TCP = get_current_tcp()
    # print("1")
    # print(TCP)
    TCP_Postion = TCP[0:3]*1000
    # print("2")
    # print(TCP_Postion)
    TCP_Rotation_Vec = TCP[3:6]
    # print("3")
    # print(TCP_Rotation_Vec)
    Camera_Calibration_RotationMatrix, Camera_Calibration_TransVector = TCPPosetoCameraPose(TCP_Rotation_Vec,TCP_Postion)

    Base_Calobration_Trans = np.array([
    [-0.991372360069160,	0.0344899310385318,	0.00167292845223808,	579.046363776787],
    [-0.0497666569959037,	0.901805219997417,	-0.00111212489025246,	-485.104685940117],
    [-0.000888232419437007,	-0.0289641764006589,	-0.958527707367941,	-7.41394645813782],
    [0, 0, 0, 1]])

    # print("4")
    # print(Camera_Calibration_RotationMatrix)
    # print("5")
    # print(Camera_Calibration_TransVector)
    Detection_Result = ObjectDetection(img)
    # Detection_Result = np.array([
    #                             [1,800.98,309],
    #                             [2,600.7,   365.65],
    #                             [2,699.93,   325.52],
    #                             [3,321,  645],
    #                             [2,    1400,   220],
    #                             [2,    1200,   713.57],
    #                             [1,    1697.1,   600],
    #                             ])
    # # Detection_Result = np.array([
    # #                             [0,715.98,232.79],
    # #                             [2,1449.7,   273.65],
    # #                             [1,693.93,   690.52],
    # #                             [1,1441.6,  732.68],
    # #                             [1,    1667.8,   295.61],
    # #                             [0,    931.08,   713.57],
    # #                             [2,      1174,   702.64],
    # #                             [2,    927.82,   240.63],
    # #                             [3,    1227.1,   272.67],
    # #                             [0,      1227,    272.8]])



    rows = Detection_Result.shape[0]

    # 创建一个新矩阵，初始化为原矩阵的第一列
    new_matrix = np.zeros((rows, 7))
    new_matrix[:, 0] = Detection_Result[:, 0]


    for i in range(rows):
        PixelResult = Detection_Result[i, 1:3]
        new_values_calibration = single2Dto3Dpt(PixelResult,Camera_Calibration_RotationMatrix,Camera_Calibration_TransVector,Camera_Instinct,0)
        # print(new_values_calibration)
        new_row = np.array([[1]])
        new_values_calibration_H = np.vstack((new_values_calibration, new_row))
        
        new_values_base_H = np.dot(Base_Calobration_Trans,new_values_calibration_H)
        new_values_base = new_values_base_H[0:3]
        new_values_base = new_values_base.reshape(1,3)
    # 将新值填入矩阵的第二到第四列
        new_matrix[i, 1:4] = new_values_base/1000
        new_matrix[i, 3:7] = [0, 2.18204119, -2.20759957,  0.06040668]
        # print(new_matrix)
        # print("new_matrix")
    return new_matrix,rows

def highvaluepick(pickup_position):
    target_tcp_p1 = pickup_position
    # target_tcp_p2 = pickup_position
    # print("pickup_position")
    # print(pickup_position)
    target_tcp_p1[2] = 0.15
    # # target_tcp_p2[2] = 0
    move_to_tcp_with_vacuum_on(target_tcp_p1)
    # print("target_tcp_p1")
    # print(target_tcp_p1)
    target_tcp_p1[2] = -0.005
    move_to_tcp_with_vacuum_on(target_tcp_p1)
    # print("target_tcp_p1")
    # print(target_tcp_p1)
    # grasp()
    target_tcp_p1[2] = 0.15
    move_to_tcp(target_tcp_p1)
    place_position_high_p1 = HighValue_Position
    # place_position_high_p2 = HighValue_Position
    place_position_high_p1[2] = 0.2
    # place_position_high_p2[2] = 0.1
    move_to_tcp(place_position_high_p1)
    # print("place_position_high_p1")
    # print(place_position_high_p1)
    place_position_high_p1[2] = 0.1
    move_to_tcp_with_vacuum_off(place_position_high_p1)
    # release()
    place_position_high_p1[2] = 0.2
    move_to_tcp_with_vacuum_off(place_position_high_p1)
    # print("place_position_high_p1")
    # print(place_position_high_p1)

def lowvaluepick(pickup_position):
    target_tcp_p1 = pickup_position
    # target_tcp_p2 = pickup_position
    target_tcp_p1[2] = 0.15
    
    move_to_tcp_with_vacuum_on(target_tcp_p1)
    # print("target_tcp_p1")
    # print(target_tcp_p1)
    target_tcp_p1[2] = -0.005
    move_to_tcp_with_vacuum_on(target_tcp_p1)
    # print("target_tcp_p1")
    # print(target_tcp_p1)
    # grasp()
    target_tcp_p1[2] = 0.15
    move_to_tcp(target_tcp_p1)
    place_position_low_p1 = LowValue_Position
    # place_position_low_p2 = LowValue_Position
    place_position_low_p1[2] = 0.2
    # place_position_low_p2[2] = 0.1
    move_to_tcp(place_position_low_p1)
    # print("place_position_low_p1")
    # print(place_position_low_p1)
    place_position_low_p1[2] = 0.1
    move_to_tcp_with_vacuum_off(place_position_low_p1)
    # release()
    place_position_low_p1[2] = 0.2
    move_to_tcp_with_vacuum_off(place_position_low_p1)
    # print("place_position_low_p1")
    # print(place_position_low_p1)

def Capture():
    camera = RealsenseD435()
    time.sleep(0.25)
    color_img = camera.get_data()
    # plt.subplot(111)
    # plt.imshow(color_img)
    # plt.show()
    return color_img

def Vacuumon():
    
    
    sh_file_path = 'VacuumOnscript.sh'  
    result = subprocess.run(['bash', sh_file_path])
    # tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.connect((HOST, PORT))

    
def Vacuumoff():
  
    sh_file_path = 'VacuumOffscript.sh'  
    result = subprocess.run(['bash', sh_file_path])
    # tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.connect((HOST, PORT))



# Image = Capture()
# Test1 = ObjectDetection(Image)
# print(Test1)

if __name__ == '__main__':
    # go_home()

    # move_to_joint(Initial_Test_Position_joint)
    # Vacuumon()
    # Vacuumon()
    # move_to_joint(Case_flip_insert_Position_Ready_joint)
    # move_to_joint(Case_flip_insert_Position_Release_Joint)
    # Vacuumoff()
    # Vacuumoff()
    # move_to_joint(Case_flip_insert_Position_Free_Joint)
    # move_to_joint(Case_flip_insert_Position_Rotation_way1_Joint)
    # move_to_joint(Case_flip_pickup_Position_Ready_Joint)
    # Vacuumon()
    # Vacuumon()
    # move_to_joint(Case_flip_pickup_Position_Grab_Joint)
    # move_to_joint(Case_flip_pickup_Position_Out_Joint)




    go_home()
    time.sleep(5)
    move_to_tcp(Initial_Test_Position_TCP)
    Vacuumon()
    Vacuumon()
    move_to_tcp(Initial_Test_Position_Upper_TCP)
    move_to_joint(Case_flip_insert_Position_Ready_joint)
    move_to_tcp(Case_flip_insert_Position_Release_TCP)
    Vacuumoff()
    Vacuumoff()
    move_to_tcp(Case_flip_insert_Position_Free_TCP)
    move_to_tcp(Case_flip_insert_Position_Rotation_way1_TCP)
    move_to_tcp(Case_flip_pickup_Position_Ready_TCP)
    Vacuumon()
    Vacuumon()
    move_to_tcp(Case_flip_pickup_Position_Grab_TCP)
    move_to_tcp(Case_flip_pickup_Position_Out_TCP)
    place_position_low_p1 = LowValue_Position
    move_to_tcp(place_position_low_p1)
    place_position_low_p1[2] = 0.03
    move_to_tcp_with_vacuum_off(place_position_low_p1)
    go_home()



    
    # go_home()
    # # img = '/home/grads/c/changliu.chris/REMADE/REMADE/001_Color.png'
    # while True:
    #     print("Image Capture")
    #     img = Capture()
    #     print("Image Capture Done")
    #     # Image2TCP(img)
    #     Sequence, TotalParts = Image2TCP(img)
        
    #     if TotalParts != 0:
    #         for i in range(TotalParts):
    #             Classification = Sequence[i,0]
    #             Target_TCP_OBJ = Sequence[i,1:7]
    #             if Classification in [0,1,3]:
    #                 lowvaluepick(Target_TCP_OBJ)
    #             elif Classification in [2,4]:
    #                 highvaluepick(Target_TCP_OBJ)
    #             else:
    #                 print("No more parts")
    #         go_home()
    #     else:
    #         go_home()
    #         print("No parts detected")
    #         time.sleep(0.5)