#!/usr/bin/env python3
"""
__main__.py

Entry point for the program.

OVERVIEW:
Responsible for the main program loop, CLI argument parsing, and initialization of 
the curses-based terminal interface. It coordinates between the metrics gathering 
functions and the display rendering.

CURSES:
This library lets us create terminal-based UI that can be updated in-place without
scrolling, allowing us a dashboard-like experience similar to htop or top.
"""

import datetime
import getopt
import os
import signal
import sys
import time
import curses
from curses import wrapper
from sys import platform

from merrin import config
from merrin.display import print_metrics
from merrin.metrics import get_uptime, get_cpu_usage, get_gpu_usage, get_meminfo, get_temp

"""
signal_handler - Interrupt signal (Ctrl+C) handler for graceful shutdown
@sig: Signal number received
@frame: Current stack frame (unused here)
"""
def signal_handler(sig, frame):
    sys.exit(0)

"""
handle_args - Parse command line arguments to configure program behavior

We use the getopt module for UNIX-style argument parsing similar to how getopt() works
in C. Putting a colon after a flag tells getopt that it requires an argument.

Return: Update interval in seconds, or None if help was displayed
"""
def handle_args():
    update_interval = config.DEFAULT_UPDATE_INTERVAL
    argv = sys.argv[1:] # Skip the program name
    try:
        opts, args = getopt.getopt(argv, "hu:")
    except:
        print("Error")
    # Process each option that was found
    for opt, arg in opts:
        if opt == '-h':
            print(f"-h\tDisplay this message\n-u\tSpecify update interval in seconds")            
            sys.exit(0)
        elif opt == '-u':
            update_interval = int(arg)
    return update_interval

"""
main_curses - Main application loop running inside the curses environment
@stdscr: The curses standard screen object
@update_interval: How many seconds to wait between metric updates
"""
def main_curses(stdscr, update_interval):
    # Initialize color support
    curses.start_color() 
    # Use terminal's default colors
    curses.use_default_colors()
    stdscr.clear()
    # Make getch() non-blocking so we don't wait for input
    stdscr.nodelay(True)
    while (True):
        # Gather all metrics into a single dictionary
        # This gives us a snapshot of the system state at this moment
        data = {
            'cpu_usage': get_cpu_usage(),
            'cpu_temp': get_temp(config.CPU_SENSOR_NAME, config.CPU_TEMP_LABEL),
            'gpu_usage': get_gpu_usage(),
            'gpu_temp': get_temp(config.GPU_SENSOR_NAME, config.GPU_TEMP_LABEL),
            'memory': get_meminfo(),
            'uptime': get_uptime(),
            'user': os.environ.get('USER'),
            'hostname': os.uname()[1],
            'current_datetime': datetime.datetime.now()
        }

        # Render the metrics to the screen
        print_metrics(stdscr, data)

        # Check if user pressed 'q' to quit (non-blocking)
        key = stdscr.getch()
        if key == ord('q'):
            break

        # Wait before next update
        time.sleep(update_interval)
        
        # Clear screen for next frame
        stdscr.erase()

"""
main - Program entry point that sets up signal handling and starts curses interface

CURSES WRAPPER:
This is important - it handles initialization and cleaning up the terminal. 
This prevents the terminal from being left in a broken state if the program crashes
or is interrupted.
"""
def main():
    # Register handler for graceful shutdown on Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # This tool relies on Linux-specific interfaces
    if platform not in ("linux", "linux2"):
        print("This program must be run on Linux")
        sys.exit(1)

    # Parse command-line arguments
    update_interval = handle_args()
    if update_interval is None:
        sys.exit(0)
    
    # Start the curses interface (wrapper handles cleanup automatically)
    wrapper(main_curses, update_interval)

if __name__ == "__main__":
    main()
