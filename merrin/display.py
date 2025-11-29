"""
display.py

Terminal display rendering using the curses library.

OVERVIEW:
Responsible for handling all visual output for the system monitor. It takes the collected metrics and 
renders them in a clean, color-coded format. 
"""

import curses

import merrin.config

"""
print_metrics - Render all system metrics to the terminal
@stdscr: The curses standard screen object
@data: Dictionary containing all collected metrics

After rendering each metric, we increment current_row to move to the next line. This is necessary
because the number of GPUs (and thus the number of rows the GPU section will take) varies by system. 
"""
def print_metrics(stdscr, data):
    current_row = 0

    #Initialize color pairs for normal and warning states. -1 means use the terminal's default colors
    curses.init_pair(1, -1, -1) # Normal: default colors
    curses.init_pair(2, curses.COLOR_RED, -1) # Warning: red text

    # HEADER
    # Displays username, hostname, and current timestamp 
    if data['user'] is not None and data['hostname'] is not None:
        stdscr.addstr(current_row, 0, f"{data['user']}@{data['hostname']} | {data['current_datetime'].month}/{data['current_datetime'].day}/{data['current_datetime'].year} {data['current_datetime'].hour:02}:{data['current_datetime'].minute:02}:{data['current_datetime'].second:02}", curses.A_BOLD)
        current_row += 1

    # CPU UTILIZATION
    stdscr.addstr(current_row, 0, "CPU Utilization:", curses.A_BOLD)
    if data['cpu_usage'] is not None:
        # Choose color based on utilization threshold, >=90% is considered heavy load
        cpu_color = curses.color_pair(1)
        if data['cpu_usage'] >= 90:
            cpu_color = curses.color_pair(2)
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['cpu_usage']}%", cpu_color)
    else: 
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
    current_row += 1
    
    # CPU TEMPERATURE
    stdscr.addstr(current_row, 0, "CPU Temperature:", curses.A_BOLD)
    if data['cpu_temp'] is not None:
        # AMD CPUs throttle around 95 celsius, but we warn the user at 85 
        ct_color = curses.color_pair(1)
        if data['cpu_temp'] >= 85:
            ct_color = curses.color_pair(2)
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['cpu_temp']} C", ct_color)
    else:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
    current_row += 1

    # GPU VRAM USAGE
    stdscr.addstr(current_row, 0, "GPU VRAM Usage:", curses.A_BOLD)
    if data['gpu_usage'] is not None:
        # Some systems have multiple GPUs, each gets its own row
        for card, usage in data['gpu_usage'].items():
            gpu_color = curses.color_pair(1)
            # We warn at >=95% VRAM usage
            if (usage['used'] / usage['total']) * 100 >= 95:
                gpu_color = curses.color_pair(2)
            stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{card}: {usage['used']} MB / {usage['total']} MB", gpu_color)
            current_row += 1
    else: 
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
        current_row += 1
    
    # GPU TEMPERATURE
    stdscr.addstr(current_row, 0, "GPU Temperature:", curses.A_BOLD)
    if data['gpu_temp'] is not None:
        gt_color = curses.color_pair(1)
        # The junction is the hottest spot on the GPU die
        # AMD GPUs typically throttle at 110 celsius at the junction, but we warn at 95
        if data['gpu_temp'] >= 95:
            gt_color = curses.color_pair(2)
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['gpu_temp']} C", gt_color)
    else:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
    current_row += 1

    # RAM USAGE
    stdscr.addstr(current_row, 0, "RAM:", curses.A_BOLD)
    if data['memory'] is not None:
        mem_color = curses.color_pair(1)
        # We warn at >=95% RAM usage
        # Linux uses swap (memory on storage devices) when RAM fills, which is substantially slower
        if (data['memory']['used'] / data['memory']['total']) * 100 >= 95:
            mem_color = curses.color_pair(2)
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['memory']['used']} MB / {data['memory']['total']} MB", mem_color)
    else: 
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
    current_row += 1

    # SYSTEM UPTIME
    # Not inherently dangerous to have a high uptime, but it is good to be aware of
    stdscr.addstr(current_row, 0, "Uptime:", curses.A_BOLD)
    if data['uptime'] is not None:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['uptime']['hours']} hours, {data['uptime']['minutes']} minutes")
    else: 
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")

    # Push all buffered changes to the terminal
    stdscr.refresh()
