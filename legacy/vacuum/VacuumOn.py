import onrobot
from onrobot import VG
import time

# Set the local device name
LOCAL_DEVICE_NAME = '/tmp/ttyUR'

device = LOCAL_DEVICE_NAME

vg = VG(device=device)
print("Turn on all vacuums.")
vg.vacuum_on(sleep_sec=1.0)

