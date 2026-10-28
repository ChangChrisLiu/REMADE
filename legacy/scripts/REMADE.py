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
    tool_acc = 2.5 # Safe: 0.5
    tool_vel = 2.5  # Safe: 0.2
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




def move_to_tcp_with_vacuum_on(target_tcp):
    tool_acc = 2.5 # Safe: 0.5
    tool_vel = 2.5 # Safe: 0.2
    tool_pos_tolerance = [0.001, 0.001, 0.001, 0.05, 0.05, 0.05]
    Vacuumon()
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





def move_to_tcp_with_vacuum_off(target_tcp):
    tool_acc = 2.5 # Safe: 0.5
    tool_vel = 2.5 # Safe: 0.2
    tool_pos_tolerance = [0.001, 0.001, 0.001, 0.05, 0.05, 0.05]
    Vacuumoff()
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
    print("rMat_inv")
    print(rMat_inv)
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
    position_tensor = result.boxes.xywhn
    position_tensor = position_tensor.to(torch.float64)
    position_np = position_tensor.cpu().numpy()
    classes_tensor = result.boxes.cls
    classes_tensor = classes_tensor.to(torch.float64)
    classes_np = classes_tensor.cpu().numpy()
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



def Image2TCP():
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
    # Detection_Result = ObjectDetection(img)
    Detection_Result = np.array([
                                [1,915.98,432.79],
                                [3,1669.7,   473.65],
                                [2,893.93,   890.52],
                                [2,1341.6,  932.68],
                                [2,    1067.8,   195.61],
                                [2,    431.08,   313.57],
                                ])
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
    # target_tcp_p2[2] = 0
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

# def Capture():
#     camera = RealsenseD435()
#     time.sleep(1)
#     color_img = camera.get_data()
#     plt.subplot(111)
#     plt.imshow(color_img)
#     plt.show()
#     return color_img

def Vacuumon():
 
    sh_file_path = 'VacuumOnscript.sh'  
    result = subprocess.run(['bash', sh_file_path], capture_output=True, text=True)

    
def Vacuumoff():
  
    sh_file_path = 'VacuumOffscript.sh'  
    result = subprocess.run(['bash', sh_file_path], capture_output=True, text=True)

# Image = Capture()
# Test1 = ObjectDetection(Image)
# print(Test1)

if __name__ == '__main__':
    # tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.connect((HOST, PORT))
    go_home()
    Image2TCP()
    # Image = Capture()
    # plt.subplot(111)
    # plt.imshow(Image)
    # plt.show()
    Sequence, TotalParts = Image2TCP()
    # # print(Image2TCP(Image))
    # print(Sequence)
    # print(TotalParts)
    if TotalParts != 0:
        for i in range(TotalParts):
            Classification = Sequence[i,0]
            Target_TCP_OBJ = Sequence[i,1:7]
            if Classification in [0,1,3]:
                lowvaluepick(Target_TCP_OBJ)
            elif Classification in [2,4]:
                highvaluepick(Target_TCP_OBJ)
            else:
                print("No more parts")
        go_home()
    else:
        go_home()
        print("No parts detected")
        time.sleep(3)
