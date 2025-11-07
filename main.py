#!/usr/bin/env python3
import getopt
import signal
import sys
import time
from curses import wrapper
from sys import platform

import config
from display import print_metrics
from metrics import get_uptime, get_cpu_usage, get_gpu_usage, get_meminfo, get_temp

def signal_handler(sig, frame):
    sys.exit(0)

def handle_args():
    update_interval = config.DEFAULT_UPDATE_INTERVAL
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hu:")
    except:
        print("Error")
    for opt, arg in opts:
        if opt == '-h':
            print(f"-h\tDisplay this message\n-u\tSpecify update interval in seconds")            
            sys.exit(0)
        elif opt == '-u':
            update_interval = int(arg)
    return update_interval

def main(stdscr, update_interval): 
    stdscr.clear()
    stdscr.nodelay(True)
    while (True):
        data = {
            'cpu_usage': get_cpu_usage(),
            'cpu_temp': get_temp(config.CPU_SENSOR_NAME, config.CPU_TEMP_LABEL),
            'gpu_usage': get_gpu_usage(),
            'gpu_temp': get_temp(config.GPU_SENSOR_NAME, config.GPU_TEMP_LABEL),
            'memory': get_meminfo(),
            'uptime': get_uptime()
        }
        print_metrics(stdscr, data)
        key = stdscr.getch()
        if key == ord('q'):
            break
        time.sleep(update_interval)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    if platform not in ("linux", "linux2"):
        print("This program must be run on Linux")
        sys.exit(1)
    update_interval = handle_args()
    if update_interval is None:
        sys.exit(0)
    wrapper(main, update_interval)
