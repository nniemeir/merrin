"""
metrics.py

System metrics collection functions.

OVERVIEW:
Contains functions that gather various system metrics by reading
from Linux pseudo-filesystems (/proc and /sys). Each function is designed
to be resilient, returning None if data collection fails rather than crashing
the application.

LINUX PSEUDO-FILESYSTEMS:
/proc - Kernel and process information
 - Files that appear to exist but are generated on-read
 - Provides current system state and statistics

/sys - Hardware and driver information
 - Structured hierarchy exposing kernel objects
 - Used here primarily for hardware sensors

ERROR HANDLING:
All functions catch FileNotFoundError and return None. This allows
the display layer to show "Unavailable" rather than crashing when 
the files cannot be read.
"""

import os
import time

import merrin.config

"""
get-uptime - Read system uptime from /proc/uptime

/proc/uptime contains two space-separated floating-point numbers
- First: Total uptime in seconds
- Second: Total idle time in seconds (sum acorss all CPU cores)

Return: dict: {'hours': int, 'minutes': int} or None if unavailable
"""
def get_uptime():
    try:
        with open(merrin.config.PROC_UPTIME_PATH) as f:
            uptime_str = f.read()
    except FileNotFoundError:
        return None
    
    # Extract the first number (total uptime in seconds)
    uptime_seconds_str = uptime_str.split()[0]
    uptime_seconds = int(float(uptime_seconds_str))

    # Convert to hours and minutes
    hours = int(uptime_seconds / 3600)
    remaining = int(uptime_seconds - (hours * 3600))
    minutes = int(remaining / 60)

    return {
    "hours": hours,
    "minutes": minutes,
    }

"""
get_info - Read memory usage statistics from /proc/meminfo

Returns: dict: {'used': int, 'total': int} in MB, or None if unavailable
"""
def get_meminfo():
    try: 
        with open(merrin.config.PROC_MEMINFO_PATH) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None
    
    # Parse the file into a dictionary
    meminfo = {}
    for line in lines:
        key, value = line.split(":")
        # Extract just the numeric value (first element after splitting spaces)
        meminfo[key.strip()] = int(value.strip().split()[0])
    
    # Calculate used memory
    # We use MemAvailable here instead of MemFree because the latter doesn't 
    # account for cache/buffers that can be reclaimed
    total = meminfo.get("MemTotal", 0)
    available = meminfo.get("MemAvailable", 0)
    used = total - available
    used_mb = int(used / 1024)
    total_mb = int(total / 1024)

    return {"used": used_mb, "total": total_mb}

"""
get_cpu_usage - Calculate cpu utilization percentage by sampling /proc/stat twice

The first line of proc stat contains many cpu metrics accumulated since boot:
cpu user nice system idle iowait irq softirq steal guest guest_nice

CATEGORIES:
- user: Normal processes in user mode
- nice: Niced (lower priority) processes in user mode
- system: Processes in kernel mode
- idle: Doing nothing
- iowait: Waiting for I/O to complete
- irq: Servicing hardware interrupts
- softirq: Servicing software interrupts
- steal: Time stolen by hypervisor (virtualization)

All of these values are in units of USER_HZ (usually 1/100th of a second).

CALCULATING USAGE:
We total all of these fields to get the total time, then total idle and iowait 
to get the idle time. Once we have sampled twice and calculated the difference between
the totals and idle totals, we get the usage percentage through this equation:
usage = 100 * (total_diff - idle_diff) / total_diff

Return: float: CPU usage percentage (0-100), or None if unavailable
"""
def get_cpu_usage():
    # FIRST MEASUREMENT
    try:
        with open(merrin.config.PROC_STAT_PATH) as f:
            lines1 = f.readlines()
    except FileNotFoundError:
        return None
    
    # Parse the first line after "cpu "
    # Split by whitespace and convert to float
    user1 = float(lines1[0].split()[1])
    nice1 = float(lines1[0].split()[2])
    system1 = float(lines1[0].split()[3])
    idle1 = float(lines1[0].split()[4])
    iowait1 = float(lines1[0].split()[5])
    irq1 = float(lines1[0].split()[6])
    softirq1 = float(lines1[0].split()[7])
    steal1 = float(lines1[0].split()[8])

    # Calcualte totals for first measurement
    total1 = user1 + nice1 + system1 + idle1 + iowait1 + irq1 + softirq1 + steal1
    idle_total1 = idle1 + iowait1

    # Wait before taking second measurement
    time.sleep(merrin.config.CPU_USAGE_INTERVAL)

    # SECOND MEASUREMENT
    try:
        with open(merrin.config.PROC_STAT_PATH) as f:
            lines2 = f.readlines()
    except FileNotFoundError:
        return None
    
    # Parse the same values from the second measurement
    user2 = float(lines2[0].split()[1])
    nice2 = float(lines2[0].split()[2])
    system2 = float(lines2[0].split()[3])
    idle2 = float(lines2[0].split()[4])
    iowait2 = float(lines2[0].split()[5])
    irq2 = float(lines2[0].split()[6])
    softirq2 = float(lines2[0].split()[7])
    steal2 = float(lines2[0].split()[8])

    # Calculate totals for second measurement
    total2 = user2 + nice2 + system2 + idle2 + iowait2 + irq2 + softirq2 + steal2
    idle_total2 = idle2 + iowait2

    # CALCULATE USAGE
    # Find total time elapsed
    total_diff = total2 - total1

    # Avoid division by zero
    if total_diff == 0:
        return 0.0;

    # Find how much idle time elapsed
    idle_diff = idle_total2 - idle_total1

    # Usage percentage = (active time / total time) * 100
    # Active time = total time - idle time
    usage = round(100 * (total_diff - idle_diff) / total_diff, 2)

    return usage

"""
get_gpu_usage - Read GPU VRAM usage for all detected AMD GPUS

We read from device/mem_info_vis_vram_used and device/mem_info_vis_vram_total,
these give us the visible VRAM (what is actually available to applications).

Both of these files contain a single integer that is the VRAM size in bytes.

Return: dict: {card_name: {'used': int, 'total': int}} in MB, or None if no GPUs
"""
def get_gpu_usage():
    gpu_usages = {}

    # Iterate through all entries in the DRM directory
    for card in os.listdir(merrin.config.DRM_ROOT):
        card_path = os.path.join(merrin.config.DRM_ROOT, card)

        # READ USED VRAM
        try:
            vram_used_path = os.path.join(card_path, merrin.config.GPU_USED_VRAM_PATH)
            
            # Skip if this isn't a GPU card (some DRM entries are display connectors)
            if not os.path.isfile(vram_used_path):
                continue
            with open(vram_used_path) as f:
                vram_used = int(f.read().strip())
        except FileNotFoundError:
            continue

        # READ TOTAL VRAM
        try:
            vram_total_path = os.path.join(card_path, merrin.config.GPU_TOTAL_VRAM_PATH)
            
            
            if not os.path.isfile(vram_total_path):
                continue

            with open(vram_total_path) as f:
                vram_total = int(f.read().strip())
        except FileNotFoundError:
            continue

        # Convert from bytes to megabytes
        vram_used_mb = int(vram_used / (1024 ** 2))
        vram_total_mb = int(vram_total / (1024 ** 2))

        # Store stats for this GPU
        gpu_usages[card] = {"used": vram_used_mb, "total": vram_total_mb}
    
    # Return None if no GPUs were found (empty dict evaluates to False)
    return gpu_usages if gpu_usages else None

"""
get_temp - Read temperature from a specific sensor in the hwmon subsystem
@sensor_name: Name of the sensor chip (e.g., "k10temp", "amdgpu")
@temp_label: Which temperature to read (e.g., "tctl", "junction")

Return: float: Temperature in degrees Celsius, or None if not found
"""
def get_temp(sensor_name, temp_label):
    # Iterate through all hardware monitoring devices
    for hwmon in os.listdir(merrin.config.HWMON_ROOT):
        hwmon_path = os.path.join(merrin.config.HWMON_ROOT, hwmon)

        # IDENTIFY SENSOR CHIP
        try:
            with open(os.path.join(hwmon_path, "name")) as f:
                name = f.read().strip()
        except FileNotFoundError:
            continue

        # Check if this is the sensor that we are looking for
        if sensor_name in name.lower():
            # Iterate through all files in this hwmon directory
            for entry in os.listdir(hwmon_path):
                # Look for temperature label files (textX_label)
                if entry.startswith("temp") and entry.endswith("_label"):
                    label_path = os.path.join(hwmon_path, entry)

                    try:
                        with open(label_path) as f:
                            label = f.read().strip()
                    except FileNotFoundError:
                        continue

                    # Check if this is the temperature that we want
                    if label.lower() == temp_label:
                        # Replace "_label" with "_input" to get the sensor reading
                        temp_input = entry.replace("_label", "_input")
                        temp_input_path = os.path.join(hwmon_path, temp_input)

                        try:
                            with open(temp_input_path) as f:
                                # Read temperature in millidegrees
                                temp_md = int(f.read().strip())
                                # Convert to degrees and round to one decimal place
                                return round(temp_md / 1000.0, 1)
                        except FileNotFoundError:
                            continue
    return None