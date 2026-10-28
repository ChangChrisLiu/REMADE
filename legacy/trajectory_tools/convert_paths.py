#!/usr/bin/env python3

import pickle 
import os
import math 

def convert_paths(source_path:str, target_path:str)->None:
    '''
    Converting the paths to be executed on the actual robot.
    '''

    with open(source_path, 'rb') as f:
        path = pickle.load(f)

    print(f'Path is: {path}')

    new_path = []
    for waypoint in path:
        waypoint[0] = waypoint[0] + math.pi/2
        new_path.append(waypoint)

    print(f'New path is: {new_path}')

    with open(target_path, 'wb') as f:
        pickle.dump(new_path, f)

if __name__ == "__main__":

    # START TO HIGH
    source_path = "./original_paths/start_to_high.pkl"
    target_path = "./paths_for_demo/start_to_high.pkl"

    convert_paths(source_path, target_path)

    # START To LOW
    source_path = "./original_paths/start_to_low.pkl"
    target_path = "./paths_for_demo/start_to_low.pkl"

    convert_paths(source_path, target_path)

    # High To Home
    source_path = "./original_paths/high_to_home.pkl"
    target_path = "./paths_for_demo/high_to_home.pkl"

    convert_paths(source_path, target_path)

    # Low To Home
    source_path = "./original_paths/low_to_home.pkl"
    target_path = "./paths_for_demo/low_to_home.pkl"

    convert_paths(source_path, target_path)




