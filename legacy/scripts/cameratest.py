import socket
import numpy as np
import cv2
import os
import time
import struct
import pyrealsense2 as rs
import matplotlib.pyplot as plt

class RealsenseD435(object):

    def __init__(self):
        self.im_height = 1080
        self.im_width = 1920
        self.intrinsics = None
        self.get_data()
        # color_img, depth_img = self.get_data()
        # print(color_img, depth_img)


    def get_data(self):
        # Return color image and depth image
        pipeline = rs.pipeline()
        config = rs.config()
        # config.enable_stream(rs.stream.depth, self.im_width, self.im_height, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, self.im_width, self.im_height, rs.format.rgb8, 8)
        profile = pipeline.start(config)
        frames = pipeline.wait_for_frames()
        # depth = frames.get_depth_frame()
        color = frames.get_color_frame()
        # depth_img=np.asarray(depth.get_data())
        color_img=np.asarray(color.get_data())
        # print(depth_img.dtype,color_img.dtype)
        # color_profile = color.get_profile()
        # cvsprofile = rs.video_stream_profile(color_profile)
        # color_intrin = cvsprofile.get_intrinsics()   # [ 640x480  p[325.14 244.014]  f[607.879 607.348]  Inverse Brown Conrady [0 0 0 0 0] ]

        # Get camera intrinsics
        

        return color_img
    

# camera = RealsenseD435()
# time.sleep(4) # Give camera some time to load data

# # while True:
# #     color_img, depth_img = camera.get_data()
# #     plt.subplot(211)
# #     plt.imshow(color_img)
# #     plt.subplot(212)
# #     plt.imshow(depth_img)
# #     plt.show()
# color_img = camera.get_data()
# plt.subplot(111)
# plt.imshow(color_img)
# # # # # plt.subplot(212)
# # # # # plt.imshow(depth_img)
# plt.show()