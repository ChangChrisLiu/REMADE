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
import rtde_control
import rtde_receive
import pickle



rtde_c = rtde_control.RTDEControlInterface("10.125.145.89")
rtde_r = rtde_receive.RTDEReceiveInterface("10.125.145.89")



HomePosition_TCP = np.array([0.61974802, -0.35125649,  0.50125062,  2.21328055, -2.21679476,  0.06541376])
HomePosition_Joint = np.array([2.43905449, -1.05648019,  0.89354164, 4.83495043, -1.58379299,  5.58296251])


Start_Point_TCP = np.array([0.57990133, -0.44711561,  0.27736907,  2.1980858, -2.23729211,  0.06219291])
Start_Point_Joint = np.array([2.30167532, -0.94790252,  1.29957039,  4.32131927, -1.5745104,   5.46153021])

High_Value_TCP = np.array([-0.63864465, -0.31121099,  0.35806142,  0.03533784, -3.1262295,  -0.01123007])
High_Value_Joint = np.array([0.2658813,  -1.04910822,  1.2415331,   4.5075566,  -1.58251459,  4.95629358])

Low_Value_TCP = np.array([-0.60798709, -0.58852783,  0.34920205, -0.0586202,  -3.09037277,  0.06728373])
Low_Value_Joint = np.array([0.60966611, -0.65365984,  0.60102302,  4.69948976, -1.56663305,  5.36124945])




Camera_Instinct = np.array([
    [1354.73552660491, 0, 970.580407580363],
    [0, 1360.53566517000, 542.269475710679],
    [0, 0, 1]])


TCP_Speed = 1.2
TCP_Accele = 1.5
Joint_Speed = 1.05
Joint_Accele = 1.4


def get_current_tcp():
    position = rtde_r.getActualTCPPose()
    return np.asarray(position)


def move_to_tcp(target_tcp):
    tool_acc = TCP_Accele # Safe: 0.5
    tool_vel = TCP_Speed# Safe: 0.2
    rtde_c.moveL(target_tcp, tool_vel, tool_acc)



def get_current_joint():
    position = rtde_r.getActualQ()
    return np.asarray(position)



def move_to_joint(target_joint):
    joint_acc = Joint_Accele # Safe: 0.5
    joint_vel = Joint_Speed  # Safe: 0.2
    rtde_c.moveJ(target_joint, joint_vel, joint_acc)



def move_to_joint_sequence(path):
    joint_velocity = Joint_Speed
    joint_acceleration = Joint_Accele
    blend = 0.02
    for row in path:
        row.extend([joint_velocity, joint_acceleration, blend])
    rtde_c.moveJ(path, asynchronous=False)




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

path_start_high = load_path_high_go()
path_start_low = load_path_low_go()
path_high_home = load_path_high_back()
path_low_home = load_path_low_back()



def move_to_tcp_with_vacuum_on(target_tcp):
    tool_acc = TCP_Accele # Safe: 0.5
    tool_vel = TCP_Speed  # Safe: 0.2
    rtde_c.moveL(target_tcp, tool_vel, tool_acc)
    Vacuumon()


def move_to_tcp_with_vacuum_off(target_tcp):
    tool_acc = TCP_Accele # Safe: 0.5
    tool_vel = TCP_Speed  # Safe: 0.2
    rtde_c.moveL(target_tcp, tool_vel, tool_acc)
    Vacuumoff()


def move_to_joint_with_vacuum_off(target_joint):
    joint_acc = Joint_Accele # Safe: 0.5
    joint_vel = Joint_Speed  # Safe: 0.2
    rtde_c.moveJ(target_joint, joint_vel, joint_acc)
    Vacuumoff()


def move_to_tcp_slow(target_tcp):
    tool_acc = 0.5 # Safe: 0.5
    tool_vel = 0.2  # Safe: 0.2
    rtde_c.moveL(target_tcp, tool_vel, tool_acc)
    


def increase_move(delta_x, delta_y, delta_z, delta_theta):
    tcp = get_current_tcp()
    rpy = util.rv2rpy(tcp[3], tcp[4], tcp[5])
    rpy[2] = rpy[2] + delta_theta
    target_rv = util.rpy2rv(rpy)
    target_tcp = np.asarray([tcp[0] + delta_x, tcp[1] + delta_y, tcp[2] + delta_z,
                             target_rv[0], target_rv[1], target_rv[2]])
    move_to_tcp_slow(target_tcp)

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
    move_to_joint_with_vacuum_off(HomePosition_Joint)



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
    high_confid_np = np.where(confid_np>0.9)
    position_np = position_np[high_confid_np]
    classes_np = classes_np [high_confid_np]
    # print(position_np)
    # print(classes_np)
    # np.set_printoptions(precision=6, floatmode='fixed')
    # Extract the first two columns of position_np.
    position_first = 1920 * position_np[:, 0]
    position_first = position_first.reshape(-1,1)
    print(position_first)

    position_second = 1080 * position_np[:, 1]
    position_second = position_second.reshape(-1,1)
    print(position_second)
    position_first_two = np.hstack((position_first,position_second))

# Reshape classes_np into a column vector for joining with position_first_two.
    classes_np_column = classes_np.reshape(-1, 1)

# Join classes_np and position_first_two horizontally.
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

    Detection_Result = ObjectDetection(img)
   
    rows = Detection_Result.shape[0]

    # Initialize a new matrix with the first column of the original matrix.
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
        print('Robot_base_position',new_values_base)
    # Fill columns two through four with the new values.
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
    move_to_joint_sequence(path_start_high)
    place_position_high_p1 = High_Value_TCP

    place_position_high_p1[2] = 0.1
    move_to_tcp_with_vacuum_off(place_position_high_p1)
    # release()
    place_position_high_p1[2] = 0.15
    move_to_tcp_with_vacuum_off(place_position_high_p1)
    time.sleep(0.01)
    move_to_joint_sequence(path_high_home)
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
    move_to_joint_sequence(path_start_low)
    place_position_low_p1 = Low_Value_TCP
    
    place_position_low_p1[2] = 0.1
    move_to_tcp_with_vacuum_off(place_position_low_p1)
    # release()
    place_position_low_p1[2] = 0.15
    move_to_tcp_with_vacuum_off(place_position_low_p1)
    time.sleep(0.01)
    move_to_joint_sequence(path_low_home)
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


if __name__ == '__main__':
    go_home()

    while True:
        print("Image Capture")
        img = Capture()
        print("Image Capture Done")
        # Image2TCP(img)
        Sequence, TotalParts = Image2TCP(img)
        
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
            
        else:
            go_home()
            print("No parts detected")
            time.sleep(0.5)
