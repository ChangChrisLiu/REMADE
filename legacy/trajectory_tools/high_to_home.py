#!/usr/bin/env python3

import urx
import time 
import math
import pickle

def connect_ur():
    '''
    connecting to the robot
    '''

    IP = '10.125.145.89'

    i, max_retry = 0, 3
    while i < max_retry:
        i = i + 1
        try:
            rob = urx.Robot(IP)
            print('Robot is connected.\n')
            return rob
        except Exception:
            print(f'Connection retry: {i}. \n')
            time.sleep(1)
            continue
        break

    if i >= max_retry:
        print('Unable to connect to the robot.')
        exit()

def load_path():
    '''
    loads the MPNet planned path
    '''

    file_name = "paths_for_demo/high_to_home.pkl"
    with open(file_name, 'rb') as f:
        path = pickle.load(f)
    
    return path, path[0], path[-1]

def move_ur5e_joints(rob, joints: list)-> None:
    '''
    move the joints
    '''

    rob.movej(joints, acc=0.1, vel=1, relative=False, wait=True)
    #rob.movep(joints, acc=0.1, vel=0.1, radius=0.05, relative=False, wait=True)

    


if __name__ == "__main__":
    '''
    The main function for moving the robot.
    '''
    try:
        rob = connect_ur()
        path, start, end = load_path()
        print(len(path))
        
        move_to_start = False
        if move_to_start:
            move_ur5e_joints(rob, path[0])
        else:
            for waypoint in path:
                move_ur5e_joints(rob, waypoint)

        print([waypoint *180 / (math.pi) for waypoint in start])
        print([waypoint *180 / (math.pi) for waypoint in end])

    finally:
        rob.close()

