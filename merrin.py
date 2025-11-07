#!/usr/bin/env python3
import time
import os
import curses
from curses import wrapper
import sys
import getopt

def get_uptime():
    try:
        with open("/proc/uptime") as f:
            uptime_str = f.read()
    except FileNotFoundError:
        return None
    uptime_seconds_str = uptime_str.split()[0]
    uptime_seconds = int(float(uptime_seconds_str))
    hours = int(uptime_seconds / 3600)
    remaining = int(uptime_seconds - (hours * 3600))
    minutes = int(remaining / 60)
    remaining = int(remaining - (minutes * 60))
    return {
    "hours": hours,
    "minutes": minutes,
    "seconds": remaining
    }

def get_meminfo():
    try: 
        with open("/proc/meminfo") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None
    meminfo = {}
    for line in lines:
        key, value = line.split(":")
        meminfo[key.strip()] = int(value.strip().split()[0])
    total = meminfo.get("MemTotal", 0)
    free = meminfo.get("MemFree", 0)
    used = total - free
    used_mb = int(used / 1024)
    total_mb = int(total / 1024)
    return {"used": used_mb, "total": total_mb}

def get_cpu_usage():
    try:
        with open("/proc/stat") as f:
            lines1 = f.readlines()
    except FileNotFoundError:
        return None
    user1 = float(lines1[0].split()[1])
    nice1 = float(lines1[0].split()[2])
    system1 = float(lines1[0].split()[3])
    idle1 = float(lines1[0].split()[4])
    iowait1 = float(lines1[0].split()[5])
    irq1 = float(lines1[0].split()[6])
    softirq1 = float(lines1[0].split()[7])
    steal1 = float(lines1[0].split()[8])
    total1 = user1 + nice1 + system1 + idle1 + iowait1 + irq1 + softirq1 + steal1
    idle_total1 = idle1 + iowait1
    time.sleep(1)
    try:
        with open("/proc/stat") as f:
            lines2 = f.readlines()
    except FileNotFoundError:
        return None
    user2 = float(lines2[0].split()[1])
    nice2 = float(lines2[0].split()[2])
    system2 = float(lines2[0].split()[3])
    idle2 = float(lines2[0].split()[4])
    iowait2 = float(lines2[0].split()[5])
    irq2 = float(lines2[0].split()[6])
    softirq2 = float(lines2[0].split()[7])
    steal2 = float(lines2[0].split()[8])
    total2 = user2 + nice2 + system2 + idle2 + iowait2 + irq2 + softirq2 + steal2
    idle_total2 = idle2 + iowait2
    total_diff = total2 - total1
    if total_diff == 0:
        return 0.0;
    idle_diff = idle_total2 - idle_total1
    usage = round(100 * (total_diff - idle_diff) / total_diff, 2)
    return usage

def get_gpu_usage():
    gpu_usages = {}
    drm_root = "/sys/class/drm"
    for card in os.listdir(drm_root):
        card_path = os.path.join(drm_root, card)
        try:
            vram_used_path = os.path.join(card_path, "device/mem_info_vis_vram_used")
            if not os.path.isfile(vram_used_path):
                continue
            with open(vram_used_path) as f:
                vram_used = int(f.read().strip())
        except FileNotFoundError:
            continue
        try:
            vram_total_path = os.path.join(card_path, "device/mem_info_vis_vram_total")
            if not os.path.isfile(vram_total_path):
                continue
            with open(vram_total_path) as f:
                vram_total = int(f.read().strip())
        except FileNotFoundError:
            continue
        vram_used_mb = int(vram_used / (1024 ** 2))
        vram_total_mb = int(vram_total / (1024 ** 2))
        gpu_usages[card] = {"used": vram_used_mb, "total": vram_total_mb}
    return gpu_usages if gpu_usages else None

def get_cpu_temp():
    hwmon_root = "/sys/class/hwmon"
    for hwmon in os.listdir(hwmon_root):
        hwmon_path = os.path.join(hwmon_root, hwmon)
        try:
            with open(os.path.join(hwmon_path, "name")) as f:
                name = f.read().strip()
        except FileNotFoundError:
            continue
        if "k10temp" in name.lower():
            for entry in os.listdir(hwmon_path):
                if entry.startswith("temp") and entry.endswith("_label"):
                    label_path = os.path.join(hwmon_path, entry)
                    try:
                        with open(label_path) as f:
                            label = f.read().strip()
                    except FileNotFoundError:
                        continue
                    if label.lower() == "tccd1":
                        temp_input = entry.replace("_label", "_input")
                        temp_input_path = os.path.join(hwmon_path, temp_input)
                        try:
                            with open(temp_input_path) as f:
                                temp_md = int(f.read().strip())
                                return round(temp_md / 1000.0, 1)
                        except FileNotFoundError:
                            continue
    return None

def get_gpu_temp():
    hwmon_root = "/sys/class/hwmon"
    for hwmon in os.listdir(hwmon_root):
        hwmon_path = os.path.join(hwmon_root, hwmon)
        try:
            with open(os.path.join(hwmon_path, "name")) as f:
                name = f.read().strip()
        except FileNotFoundError:
            continue
        if "amdgpu" in name.lower():
            for entry in os.listdir(hwmon_path):
                if entry.startswith("temp") and entry.endswith("_label"):
                    label_path = os.path.join(hwmon_path, entry)
                    try:
                        with open(label_path) as f:
                            label = f.read().strip()
                    except FileNotFoundError:
                        continue
                    if label.lower() == "junction":
                        temp_input = entry.replace("_label", "_input")
                        temp_input_path = os.path.join(hwmon_path, temp_input)
                        try:
                            with open(temp_input_path) as f:
                                temp_md = int(f.read().strip())
                                return round(temp_md / 1000.0, 1)
                        except FileNotFoundError:
                            continue
    return None

def print_metrics(stdscr):
    for row in range(6):
        for col in range(17, 64):
            stdscr.addstr(row, col, " ")
    current_row = 0
    stdscr.addstr(current_row, 0, "CPU Utilization:", curses.A_BOLD)
    usage = get_cpu_usage()
    if usage is not None:
        stdscr.addstr(current_row, 17, f"{usage}%")
    else: 
        stdscr.addstr(current_row, 17, "Unavailable")
    current_row += 1
    stdscr.addstr(current_row, 0, "CPU Temperature:", curses.A_BOLD)
    cpu_temp = get_cpu_temp()
    if cpu_temp is not None:
        stdscr.addstr(current_row, 17, f"{cpu_temp} C")
    else:
        stdscr.addstr(current_row, 17, "Unavailable")
    current_row += 1
    stdscr.addstr(current_row, 0, "GPU VRAM Usage:", curses.A_BOLD)
    gpu_usages = get_gpu_usage()
    if gpu_usages is not None:
        for card, usage in gpu_usages.items():
            stdscr.addstr(current_row, 17, f"{card}: {usage['used']} MB / {usage['total']} MB")
            current_row += 1
    else: 
        stdscr.addstr(current_row, 17, "Unavailable")
        current_row += 1
    stdscr.addstr(current_row, 0, "GPU Temperature:", curses.A_BOLD)
    gpu_temp = get_gpu_temp()
    if gpu_temp is not None:
        stdscr.addstr(current_row, 17, f"{gpu_temp} C")
    else:
        stdscr.addstr(current_row, 17, "Unavailable")
    current_row += 1
    stdscr.addstr(current_row, 0, "RAM:", curses.A_BOLD)
    memory_info = get_meminfo()
    if memory_info is not None:
        stdscr.addstr(current_row, 17, f"{memory_info['used']} MB / {memory_info['total']} MB")
    else: 
        stdscr.addstr(current_row, 17, "Unavailable")
    current_row += 1
    stdscr.addstr(current_row, 0, "Uptime:", curses.A_BOLD)
    uptime = get_uptime()
    if uptime is not None:
        stdscr.addstr(current_row, 17, f"{uptime['hours']} hours, {uptime['minutes']} minutes")
    else: 
        stdscr.addstr(current_row, 17, "Unavailable")
    stdscr.refresh()

def handle_args(stdscr):
    update_interval = 1
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hu:")
    except:
        print("Error")

    for opt, arg in opts:
        if opt == '-h':
            stdscr.addstr(0, 0, f"-h\tDisplay this message")
            stdscr.addstr(1, 0, f"-u\tSpecify update interval in seconds")
            while (True):
                key = stdscr.getch()
                if key == ord('q'):            
                    sys.exit()
        elif opt == '-u':
            update_interval = int(arg)
    return update_interval

def main(stdscr):
    stdscr.clear()
    update_interval = handle_args(stdscr)
    if update_interval is None:
        return
    while (True):
        print_metrics(stdscr)
        key = stdscr.getch()
        if key == ord('q'):
            break
        time.sleep(update_interval)

wrapper(main)
