import subprocess
import time
import rclpy
from rclpy.node import Node
import urx
from std_srvs.srv import Trigger
import time
import collections
collections.Iterable = collections.abc.Iterable
from onrobot import VG
import cv2
import numpy as np
from ultralytics import YOLO
from cameratest import RealsenseD435


HomePosition = np.array([0.40974318,-0.3043783, 0.42603075,  2.18204119, -2.20759957,  0.14040668])
HighValue_Position = np.array([-0.33768291, -0.61855289,  0.00431814, -0.85744133,  3.01975499, -0.11043932])
LowValue_Position = np.array([-0.37072683, -0.29942229,  0.00312853,  0.07627575, -3.11429522,  0.13188759])






Camera_Instinct = np.array([
    [1353.37961859407, 0, 972.468374798104],
    [0, 1354.49471811200, 544.964374706436],
    [0, 0, 1]])







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




# print("1")

# class UR5eController(Node):
#     def __init__(self):
#         super().__init__('ur5e_controller')
#         self.robot = urx.Robot("192.168.1.2")  # Replace with your robot's IP address
#         self.create_service(Trigger, 'move_home', self.move_home_callback)
#         self.get_logger().info('UR5e Controller node has been started.')

#     def move_home_callbzack(self, request, response):
#         self.get_logger().info('Moving to home position...')
#         self.robot.movej((0, -1.57, 1.57, 0, 1.57, 0), acc=0.1, vel=0.2)
#         response.success = True
#         response.message = "Moved to home position."
#         return response

# def main(args=None):
#     rclpy.init(args=args)
#     controller = UR5eController()
#     rclpy.spin(controller)
#     controller.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()

def connect_ur(ip):
   ''' Connect to the robot. '''
   i, max_retry = 0, 3
   while i < max_retry:
       i += 1
       try:
           robot_connected = urx.Robot(ip)
           print("Robot is connected. \n")
           return robot_connected
       except Exception:
           print("Connection retry. \n", i)
           time.sleep(1)
           continue
       break
   if i >= max_retry:
       print("Unable to connect to robot. \n")
       exit()


def move_L(waypoint, a=0.05, v=0.5, relative=False, threshold=0.001):
   ''' Send a move command (tcp pose) to robot. '''
   if relative:
       pose = rob.getl()
       waypoint= [v + pose[i] for i, v in enumerate(waypoint)]

   rob.movel(waypoint, acc=a, vel=v, relative=False, wait=False, threshold=threshold)
   while True:
       error = rob._get_dist(waypoint, False)
       if error < threshold:
           break


if __name__ == '__main__':

   # You should open a new terminal and run roscore first before defining the ros node.
#    rospy.init_node('ur5e', anonymous=True)
   IP = '169.254.99.10'  # use the ip address of your robot
   rob = connect_ur(IP)
#    rob.set_tcp((0, 0, 0, 0, 0, 0))   # set the tcp and payload
#    rob.set_payload(1.04, (0, 0, 0.057))
   time.sleep(0.2)

   pose = rob.getj()  # get current joint value
   print("Current joint value: \n", pose)
   tcp_pose = rob.getl()  # get current tcp pose (x, y, z, rx, ry, rz), check this to get coordinates of different waypoints.
   print("Current tcp pose: \n", tcp_pose)

#    move_L([0.1,0,0,0,0,0], relative=True)
#    rob.movel([0.1,0,0,0,0,0], relative=True, wait=False)


