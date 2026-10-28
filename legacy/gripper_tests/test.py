
import rclpy
from rclpy.node import Node
import urx
from std_srvs.srv import Trigger
import time
import collections
collections.Iterable = collections.abc.Iterable
import math
from onrobot import VG

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
   rob.set_tcp((0, 0, 0.171, 0, 0, 0))   # set the tcp and payload
   rob.set_payload(1.04, (0, 0, 0.057))
   time.sleep(0.2)

   pose = rob.getj()  # get current joint value
   print("Current joint value: \n", pose)
   tcp_pose = rob.getl()  # get current tcp pose (x, y, z, rx, ry, rz), check this to get coordinates of different waypoints.
   print("Current tcp pose: \n", tcp_pose)

#    move_L([0.1,0,0,0,0,0], relative=True)
#    rob.movel([0.1,0,0,0,0,0], relative=True, wait=False)
