import subprocess
import time
# import rclpy
# from rclpy.node import Node
# import urx
from std_srvs.srv import Trigger
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


HOST = "169.254.99.10"

PORT = 30003



HomePosition = np.array([0.40974318,-0.3043783, 0.42603075,  2.18204119, -2.20759957,  0.14040668])
HighValue_Position = np.array([-0.33768291, -0.61855289,  0.1531814, -0.85744133,  3.01975499, -0.11043932])
LowValue_Position = np.array([-0.37072683, -0.29942229,  0.1512853,  0.07627575, -3.11429522,  0.13188759])

Camera_Instinct = np.array([
    [1353.37961859407, 0, 972.468374798104],
    [0, 1354.49471811200, 544.964374706436],
    [0, 0, 1]])





def get_current_tcp():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    data = tcp_socket.recv(1108)
    position = struct.unpack('!6d', data[444:492])
    tcp_socket.close()
    return np.asarray(position)


def move_to_tcp(target_tcp):
    tool_acc = 1.2  # Safe: 0.5
    tool_vel = 0.25  # Safe: 0.2
    tool_pos_tolerance = [0.001, 0.001, 0.001, 0.05, 0.05, 0.05]
    tcp_command = "movel(p[%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=0,r=0)\n" % (
        target_tcp[0], target_tcp[1], target_tcp[2], target_tcp[3], target_tcp[4],
        target_tcp[5],
        tool_acc, tool_vel)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    tcp_socket.send(str.encode(tcp_command))  # 利用字符串的encode方法编码成bytes，默认为utf-8类型
    tcp_socket.close()
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
    move_to_tcp(target_tcp)


def get_digital_output():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    data = tcp_socket.recv(1108)
    tool = struct.unpack('!d', data[1044:1052])[0]
    tcp_socket.close()
    return tool

def move_down():
    
    tcp = get_current_tcp()
    increase_move(0,0,-0.01,0)


def move_up():
    tcp = get_current_tcp()
    increase_move(0,0,0.05,0)


def grasp():
    Vacuumon()
    move_down()
    move_up()


def release():
    Vacuumoff()
    move_up()



def go_home():
    Vacuumoff()
    move_to_tcp(HomePosition)




def TCPPosetoCameraPose(TCP_Rotation_Vec, TCP_Postion):
    TCP_Camera_Trans = np.array([
    [0.00274393113275406, -0.999999998990422, -0.0416884444835206, 107.277001220771],
    [0.999999999313138,	-0.00872913762345579, 0.0229621131598106, -30.7363324526424],
    [-0.0229120716993626, -0.0229329785581929, 0.999999999768125, 113.621536985381],
    [0, 0, 0, 1]])


    Base_Calobration_Trans = np.array([
    [-0.996262737492519,	0.0176946940623445,	-0.00272695930103513,	552.588236133681],
    [0.0177064523614100,	0.999452891522935,	-0.00664930796694823,	-486.457544406452],
    [-0.00943020029248840,	-0.0152538637642669,	-0.999589395763261,	-10.6291864462992],
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
    kMat_inv = np.linalg.inv(cameraMat)
    
    # Perform the matrix multiplications
    tempMat = np.matmul(rMat_inv, kMat_inv)
    tempMat = np.matmul(tempMat, uvPoint)
    tempMat2 = np.matmul(rMat_inv, tVec)
    
    # Calculate the scale factor to determine the Z coordinate
    s = (height + tempMat2[2, 0]) / tempMat[2, 0]
    
    # Calculate the 3D coordinates
    p = tempMat * s - tempMat2
    
    # Return the 3D point as a flattened array
    point3D = p.flatten()
    return point3D



def ObjectDetection(img):
    model = YOLO('smallmodeldet.pt')
    results = model(img)
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        # masks = result.masks 
    position_tensor = result.boxes.xywh
    position_tensor = position_tensor.to(torch.float64)
    position_np = position_tensor.cpu().numpy()
    classes_tensor = result.boxes.cls
    classes_tensor = classes_tensor.to(torch.float64)
    classes_np = classes_tensor.cpu().numpy()
    # print(position_np)
    # print(classes_np)
    # np.set_printoptions(precision=6, floatmode='fixed')
    # 只提取 position_np 的前两个数据
    position_first_two = position_np[:, :2]

# 将 classes_np 重塑为列向量，以便与 position_first_two 进行合并
    classes_np_column = classes_np.reshape(-1, 1)

# 将 classes_np 与 position_first_two 水平合并
    result_matrix = np.hstack((classes_np_column, position_first_two))
    # np.set_printoptions(suppress=True, precision=6, floatmode='fixed')
    # print(result_matrix)
    return result_matrix



def Image2TCP(img):
    TCP = get_current_tcp()
    TCP_Postion = TCP[0:3]*1000
    TCP_Rotation_Vec = TCP[3:6]
    Camera_Calibration_RotationMatrix, Camera_Calibration_TransVector = TCPPosetoCameraPose(TCP_Rotation_Vec,TCP_Postion)
    Detection_Result = ObjectDetection(img)
    rows = Detection_Result.shape[0]

    # 创建一个新矩阵，初始化为原矩阵的第一列
    new_matrix = np.zeros((rows, 7))
    new_matrix[:, 0] = Detection_Result[:, 0]


    for i in range(rows):
        PixelResult = Detection_Result[i, 1:3]
        new_values = single2Dto3Dpt(PixelResult,Camera_Calibration_RotationMatrix,Camera_Calibration_TransVector,Camera_Instinct,0)
    
    # 将新值填入矩阵的第二到第四列
        new_matrix[i, 1:4] = new_values/1000
        new_matrix[i, 4:7] = [2.18204119, -2.20759957,  0.06040668]
    return new_matrix,rows

def highvaluepick(pickup_position):
    target_tcp = pickup_position
    move_to_tcp(target_tcp)
    grasp()
    move_up()
    place_position_high = HighValue_Position
    move_to_tcp(place_position_high)
    release()

def lowvaluepick(pickup_position):
    target_tcp = pickup_position
    move_to_tcp(target_tcp)
    grasp()
    move_up()
    place_position_low = LowValue_Position
    move_to_tcp(place_position_low)
    release()

def Capture():
    camera = RealsenseD435()
    color_img = camera.get_data()
    return color_img

def Vacuumon():
 
    sh_file_path = '/VacuumFunction/VacuumOnscript.sh'  

    try:
        subprocess.run(['bash', sh_file_path], check=True)
        print("All Vacuum On")
    except subprocess.CalledProcessError as e:
        print(f"Script execution failed with return code {e.returncode}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    
def Vacuumoff():
  
    sh_file_path = '/VacuumFunction/VacuumOffscript.sh'  

    try:
        subprocess.run(['bash', sh_file_path], check=True)
        print("All Vacuum Off")
    except subprocess.CalledProcessError as e:
        print(f"Script execution failed with return code {e.returncode}")
    except Exception as e:
        print(f"An error occurred: {e}")


# if __name__ == '__main__':
#     go_home()
#     Image = Capture()
#     Sequence,TotalParts = Image2TCP(Image)
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
#     else:
#         print("No parts detected")
#         time.sleep(3)
