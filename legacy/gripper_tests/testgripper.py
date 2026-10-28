import urx  
from urx.urscript import URScript
import time
import rclpy
from rclpy.node import Node
import collections
collections.Iterable = collections.abc.Iterable

def send_urscript_command(robot,script):
    print(f"Sending URScript Command:{script}")
    robot.send_program(script)
    time.sleep(0.5)
    print("Command Sent")

def grip_gripper(robot,channel=2,vacuum=60,timeout=0,alert=True,tool_index=1):
    urscript_command = f'''vg10_grip({channel},{vacuum},{timeout},{str(alert).lower()},{tool_index})'''
    send_urscript_command(robot,urscript_command)




def release_gripper(robot,channel=2,timeout=0,autoidle=True,tool_index=1):
    urscript_command = f'''vg10_release({channel},{timeout},{str(autoidle).lower()},{tool_index})'''
    send_urscript_command(robot,urscript_command)


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
       pose = robot.getl()
       waypoint= [v + pose[i] for i, v in enumerate(waypoint)]

   robot.movel(waypoint, acc=a, vel=v, relative=False, wait=False, threshold=threshold)
   while True:
       error = robot._get_dist(waypoint, False)
       if error < threshold:
           break


if __name__ == '__main__':

   # You should open a new terminal and run roscore first before defining the ros node.
#    rospy.init_node('ur5e', anonymous=True)
   IP = '169.254.99.10'  # use the ip address of your robot
   robot = connect_ur(IP)
   robot.set_tcp((0, 0, 0.173, 0, 0, 0))   # set the tcp and payload
   robot.set_payload(1.04, (0, 0, 0.057))
   time.sleep(0.2)

   pose = robot.getj()  # get current joint value
   print("Current joint value: \n", pose)
   tcp_pose = robot.getl()  # get current tcp pose (x, y, z, rx, ry, rz), check this to get coordinates of different waypoints.
   print("Current tcp pose: \n", tcp_pose)

   grip_gripper(robot,channel=2,vacuum=60,timeout=0,alert=True,tool_index=1)
  
   release_gripper(robot,channel=2,timeout=5,autoidle=True,tool_index=1)


#    move_L([0.1,0,0,0,0,0], relative=True)
#    rob.movel([0.1,0,0,0,0,0], relative=True, wait=False)


