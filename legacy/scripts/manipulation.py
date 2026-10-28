#!/usr/bin/env python3

import rospy
import urx
from urx.robotiq_two_finger_gripper import Robotiq_Two_Finger_Gripper
from sklearn.metrics import mean_squared_error
import time
import math


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

def move_P(waypoint, a=0.05, v=0.5, relative=False, threshold=0.05):
   ''' Send a move command (tcp pose) to robot. '''
   if relative:
       pose = rob.getl()
       waypoint= [v + pose[i] for i, v in enumerate(waypoint)]

   rob.movep(waypoint, acc=a, vel=v, relative=False, wait=False, threshold=threshold)
   while True:
       error = rob._get_dist(waypoint, False)
       if error < threshold:
           break

def move_J(waypoint, a=0.5, v=0.3, relative=False, threshold=0.001):
   ''' Send a move command (joints' configuration) to robot. '''   
   if relative:
       pose = rob.getj()
       waypoint= [v + pose[i] for i, v in enumerate(waypoint)]

   rob.movej(waypoint, acc=a, vel=v, relative=False, wait=False, threshold=threshold)
   while True:
       current = rob.getj()
       rms = mean_squared_error(current, waypoint, squared=False)
       if rms < threshold:
           break

def open_gripper():
   '''
       Send a open command to gripper.
       Command out line 183-184 in source file robotiq_two_finger_gripper.py:
           # urscript._set_robot_activate()
           # urscript._set_gripper_activate()
       Activate the gripper via control panel before use.
   '''
   robotiqgrip.open_gripper()

def close_gripper():
   '''
       Send a close command to gripper.
       Command out line 183-184 in source file robotiq_two_finger_gripper.py:
           # urscript._set_robot_activate()
           # urscript._set_gripper_activate()
       Activate the gripper via control panel before use.
   '''
   robotiqgrip.close_gripper()

def gripper_action(value):
   '''
       Set gripper to a certain value (0-255):
           0: fully open.
           255: fully close.
   '''
   robotiqgrip.gripper_action(value)

def reset():
   move_L([0.08624279092689524, -0.1345775841124268, 0.33510172924051806, -2.2186697432771814, 2.2236144174830734, 0])

def demo():
   ''' A quick demo. '''
   a = 0.5
   v = 0.08
   reset()
   close_gripper()
   move_L([0.49515619996638627, 0.04554386519322387, 0.22272307716805795, -2.2186697432771814, 2.2236144174830734, 0], a=a, v=v)
   gripper_action(120)
   move_L([0,0,-0.15,0,0,0], relative=True)
   close_gripper()
   move_L([0,0,0.15,0,0,0], relative=True)
   move_L([0.2197097748768658, -0.33682882787662477, 0.22272307716805795, -2.2186697432771814, 2.2236144174830734, 0])

if __name__ == '__main__':

   # You should open a new terminal and run roscore first before defining the ros node.
   rospy.init_node('ur5e', anonymous=True)
   IP = '192.168.1.9'  # use the ip address of your robot
   rob = connect_ur(IP)
   rob.set_tcp((0, 0, 0.171, 0, 0, 0))   # set the tcp and payload
   rob.set_payload(1.04, (0, 0, 0.057))
   robotiqgrip = Robotiq_Two_Finger_Gripper(rob)
   time.sleep(0.2)

   pose = rob.getj()  # get current joint value
   print("Current joint value: \n", pose)
   tcp_pose = rob.getl()  # get current tcp pose (x, y, z, rx, ry, rz), check this to get coordinates of different waypoints.
   print("Current tcp pose: \n", tcp_pose)