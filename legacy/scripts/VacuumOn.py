# import onrobot
from onrobot import VG
# import subprocess
import time


# def start_socat():
#     UR_ip = '10.125.145.89'
#     LOCAL_DEVICE_NAME = '/tmp/ttyUR'
#     socat_command = f"socat pty,link=/tmp/ttyUR,raw,ignoreeof,waitslave tcp:${UR_ip}:54321 &"
#     socat_process = subprocess.Popen(socat_command,shell=True)
#     time.sleep(0.3)
    
#     # stdout,stderr = socat_process.communicate()


# start_socat()


# Set the local device name
LOCAL_DEVICE_NAME = '/tmp/ttyUR'

device = LOCAL_DEVICE_NAME

vg = VG(device=device)
print("Turn on all vacuums.")
vg.vacuum_on(sleep_sec=0.05)

