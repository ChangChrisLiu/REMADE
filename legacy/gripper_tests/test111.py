from urx.urscript import URScript
import socket
import math
import time
import urx
import sys

# Boilerplate URScript setup for the robot
boilerplate =  """
  set_standard_analog_input_domain(0, 1)
  set_standard_analog_input_domain(1, 1)
  set_tool_analog_input_domain(0, 1)
  set_tool_analog_input_domain(1, 1)
  set_analog_outputdomain(0, 0)
  set_analog_outputdomain(1, 0)
  set_tool_voltage(0)
  set_input_actions_to_default()
  set_tcp(p[0.0,0.0,0.0,0.0,0.0,0.0])
  set_payload(0.0)
  set_gravity([0.0, 0.0, 9.82])
  # VGC10 specific initial setup
  set_tool_voltage(24)
  set_tcp(p[0,0,0.173,0,-0,0])
  """

# Custom URScript class for the VGC10 gripper
class VGC10GripperScript(URScript):

    def __init__(self):
        super(VGC10GripperScript, self).__init__()
        # Copy the boilerplate to the start of the script to make the grip and release functions available
        self.add_line_to_program(boilerplate)

    def grip_command(self, channel=2, vacuum=60, timeout=5, alert=True, tool_index=1):
        self.add_line_to_program(f"vg10_grip({channel}, {vacuum}, {timeout}, {str(alert).lower()}, {tool_index})")

    def release_command(self, channel=2, timeout=5, autoidle=True, tool_index=1):
        self.add_line_to_program(f"vg10_release({channel}, {timeout}, {str(autoidle).lower()}, {tool_index})")

# VGC10 gripper class
class VGC10Gripper(object):

    def __init__(self, robot):
        self.robot = robot

    def grip(self, channel=2, vacuum=60, timeout=5, alert=True, tool_index=1, wait=2):
        urscript = VGC10GripperScript()
        urscript.grip_command(channel, vacuum, timeout, alert, tool_index)
        self.robot.send_program(urscript())
        time.sleep(wait)

    def release(self, channel=2, timeout=5, autoidle=True, tool_index=1, wait=2):
        urscript = VGC10GripperScript()
        urscript.release_command(channel, timeout, autoidle, tool_index)
        self.robot.send_program(urscript())
        time.sleep(wait)

    @property
    def vacuum_status(self, channel):
        # Read vacuum status for the given channel
        if channel == 0:
            return self.robot.get_analog_in(0)
        elif channel == 1:
            return self.robot.get_analog_in(1)
        else:
            raise ValueError("Invalid channel")

if __name__ == '__main__':
    rob = urx.Robot("169.254.99.10")
    gripper = VGC10Gripper(rob)

    # Example usage: Grip an object
    gripper.grip(channel=2, vacuum=60, timeout=5, alert=True, tool_index=1)
    time.sleep(2)
    # Example usage: Release the object
    gripper.release(channel=2, timeout=5, autoidle=True, tool_index=1)

    rob.close()
    print("Operation completed")
    sys.exit()
