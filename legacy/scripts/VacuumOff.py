import onrobot
from onrobot import VG
import time

# Set the local device name
LOCAL_DEVICE_NAME = '/tmp/ttyUR'

device = LOCAL_DEVICE_NAME

vg = VG(device=device)
vg.release_vacuum()
# print("Turn on all vacuums.")