import os
import time

import merrin.config

def get_uptime():
    try:
        with open(merrin.config.PROC_UPTIME_PATH) as f:
            uptime_str = f.read()
    except FileNotFoundError:
        return None
    uptime_seconds_str = uptime_str.split()[0]
    uptime_seconds = int(float(uptime_seconds_str))
    hours = int(uptime_seconds / 3600)
    remaining = int(uptime_seconds - (hours * 3600))
    minutes = int(remaining / 60)
    return {
    "hours": hours,
    "minutes": minutes,
    }

def get_meminfo():
    try: 
        with open(merrin.config.PROC_MEMINFO_PATH) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None
    meminfo = {}
    for line in lines:
        key, value = line.split(":")
        meminfo[key.strip()] = int(value.strip().split()[0])
    total = meminfo.get("MemTotal", 0)
    available = meminfo.get("MemAvailable", 0)
    used = total - available
    used_mb = int(used / 1024)
    total_mb = int(total / 1024)
    return {"used": used_mb, "total": total_mb}

def get_cpu_usage():
    try:
        with open(merrin.config.PROC_STAT_PATH) as f:
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
    time.sleep(merrin.config.CPU_USAGE_INTERVAL)
    try:
        with open(merrin.config.PROC_STAT_PATH) as f:
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
    for card in os.listdir(merrin.config.DRM_ROOT):
        card_path = os.path.join(merrin.config.DRM_ROOT, card)
        try:
            vram_used_path = os.path.join(card_path, merrin.config.GPU_USED_VRAM_PATH)
            if not os.path.isfile(vram_used_path):
                continue
            with open(vram_used_path) as f:
                vram_used = int(f.read().strip())
        except FileNotFoundError:
            continue
        try:
            vram_total_path = os.path.join(card_path, merrin.config.GPU_TOTAL_VRAM_PATH)
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

def get_temp(sensor_name, temp_label):
    for hwmon in os.listdir(merrin.config.HWMON_ROOT):
        hwmon_path = os.path.join(merrin.config.HWMON_ROOT, hwmon)
        try:
            with open(os.path.join(hwmon_path, "name")) as f:
                name = f.read().strip()
        except FileNotFoundError:
            continue
        if sensor_name in name.lower():
            for entry in os.listdir(hwmon_path):
                if entry.startswith("temp") and entry.endswith("_label"):
                    label_path = os.path.join(hwmon_path, entry)
                    try:
                        with open(label_path) as f:
                            label = f.read().strip()
                    except FileNotFoundError:
                        continue
                    if label.lower() == temp_label:
                        temp_input = entry.replace("_label", "_input")
                        temp_input_path = os.path.join(hwmon_path, temp_input)
                        try:
                            with open(temp_input_path) as f:
                                temp_md = int(f.read().strip())
                                return round(temp_md / 1000.0, 1)
                        except FileNotFoundError:
                            continue
    return None