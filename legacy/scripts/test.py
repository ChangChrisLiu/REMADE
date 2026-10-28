import numpy as np
import socket
import time
import struct
import util
import rtde

HOST = "10.125.145.89"

PORT = 30003

target_joint_1 = np.array([-0.97497589, -2.36432614, -0.8744694,  -3.09183325,  0.55743265,  1.62291861])
target_joint_2 = np.array([-0.97497589, -2.36432614, -0.34694,  -3.09183325,  0.55743265,  1.62291861])


def get_current_tcp():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    data = tcp_socket.recv(1108)
    position = struct.unpack('!6d', data[444:492])
    tcp_socket.close()
    return np.asarray(position)


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
    tcp_socket.send(str.encode(tcp_command))  # Encode the command as bytes using the default UTF-8 encoding.
    tcp_socket.close()
    # Wait until the target is reached before sending the next command.
    actual_pos = get_current_tcp()
    target_rpy = util.rv2rpy(target_tcp[3], target_tcp[4], target_tcp[5])
    rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
    while not (all([np.abs(actual_pos[j] - target_tcp[j]) < tool_pos_tolerance[j] for j in range(3)])
               and all([np.abs(rpy[j] - target_rpy[j]) < tool_pos_tolerance[j+3] for j in range(3)])):
        actual_pos = get_current_tcp()
        rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
        time.sleep(0.01)



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





def get_current_pos():  # x, y, theta
    tcp = get_current_tcp()
    rpy = util.rv2rpy(tcp[3], tcp[4], tcp[5])
    return np.asarray([tcp[0], tcp[1], rpy[-1]])




r = get_current_tcp()
joint = get_current_joint()

r_new = ', '.join(map(str,r))
joint_new = ', '.join(map(str,joint))

# test = struct.unpack('!6d', data[0:492])

print(f"[{joint_new}]")
print(joint)
print("joint")

# move_to_joint(target_joint_1)

# move_j(target_joint_1)

# r[2] = 0.42
# move_to_tcp(r)

# y = get_current_pos()



print(f"[{r_new}]")
print(r)
print("tcp")
# print(y)
# print("pos")



