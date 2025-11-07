import curses

import merrin.config

def print_metrics(stdscr, data):
    current_row = 0

    if data['user'] is not None and data['hostname'] is not None:
        stdscr.addstr(current_row, 0, f"{data['user']}@{data['hostname']} | {data['current_datetime'].month}/{data['current_datetime'].day}/{data['current_datetime'].year} {data['current_datetime'].hour:02}:{data['current_datetime'].minute:02}:{data['current_datetime'].second:02}", curses.A_BOLD)
        current_row += 1

    stdscr.addstr(current_row, 0, "CPU Utilization:", curses.A_BOLD)
    if data['cpu_usage'] is not None:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['cpu_usage']}%")
    else: 
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
    current_row += 1
    
    stdscr.addstr(current_row, 0, "CPU Temperature:", curses.A_BOLD)
    if data['cpu_temp'] is not None:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['cpu_temp']} C")
    else:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
    current_row += 1

    stdscr.addstr(current_row, 0, "GPU VRAM Usage:", curses.A_BOLD)
    if data['gpu_usage'] is not None:
        for card, usage in data['gpu_usage'].items():
            stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{card}: {usage['used']} MB / {usage['total']} MB")
            current_row += 1
    else: 
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
        current_row += 1
    
    stdscr.addstr(current_row, 0, "GPU Temperature:", curses.A_BOLD)
    if data['gpu_temp'] is not None:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['gpu_temp']} C")
    else:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
    current_row += 1

    stdscr.addstr(current_row, 0, "RAM:", curses.A_BOLD)
    if data['memory'] is not None:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['memory']['used']} MB / {data['memory']['total']} MB")
    else: 
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")
    current_row += 1

    stdscr.addstr(current_row, 0, "Uptime:", curses.A_BOLD)
    if data['uptime'] is not None:
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, f"{data['uptime']['hours']} hours, {data['uptime']['minutes']} minutes")
    else: 
        stdscr.addstr(current_row, merrin.config.FIELD_TWO_COL, "Unavailable")

    stdscr.refresh()
