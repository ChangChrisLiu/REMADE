#!/usr/bin/env python3

import argparse
from onrobot import VG
import time


# Set the local device name
LOCAL_DEVICE_NAME = '/tmp/ttyUR'

device = LOCAL_DEVICE_NAME
# device = '/tmp/ttyUR'

def run_demo(device):
    """Runs pump on/off demonstration once."""
    vg = VG(device=device)

    print("Turn on all vacuums.")
    vg.vacuum_on(sleep_sec=5.0)
    vg.release_vacuum()

    print("Turn on vacuum on channel A.")
    vg.vacuum_on_channelA(sleep_sec=5.0)
    vg.release_vacuum_channelA()

    print("Turn on vacuum on channel B.")
    vg.vacuum_on_channelB(sleep_sec=5.0)
    vg.release_vacuum_channelB()

    vg.close_connection()

if __name__ == '__main__':
    run_demo(LOCAL_DEVICE_NAME)