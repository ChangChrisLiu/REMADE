import urx
import collections
import time
collections.Iterable = collections.abc.Iterable


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



IP = '169.254.99.10'  # use the ip address of your robot
rob = connect_ur(IP)
print(rob)
time.sleep(0.2)

pose = rob.getj()  # get current joint value
print("Current joint value: \n", pose)
tcp_pose = rob.getl()  # get current tcp pose (x, y, z, rx, ry, rz), check this to get coordinates of different waypoints.
print("Current tcp pose: \n", tcp_pose)