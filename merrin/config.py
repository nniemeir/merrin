"""
config.py

Configuration constants for the system monitor. 

OVERVIEW:
Centralizes all configuration values used throughout the program. 

LINUX SYSTEM INTERFACES:
We rely on several pseudo-filesystems that Linux provides to gather system information:

/proc - Process and system information
  - Virtual filesystem providing kernel and process data
  - Files appear to exist but are generated on read by the kernel

/sys - Device and driver information
  - Exposes kernel objects as a hierarchy
  - Used here to access hardware monitoring sensors
"""

# DISPLAY CONFIGURATION
# The reported metrics appear 17 characters in to their respective rows
# This gives us a clean two-column layout:
# Column 1: Metric labels
# Column 2: Metric values
FIELD_TWO_COL = 17 

# TIMING CONFIGURATION
# How often to refresh the display (in seconds)
DEFAULT_UPDATE_INTERVAL = 1

# How long to wait between CPU measurements for usage calculation
# CPU usage requires two measurements to calculate the difference
CPU_USAGE_INTERVAL = 1

# PROC FILESYSTEM PATHS
# /proc/meminfo provides detailed memory statistics
PROC_MEMINFO_PATH = "/proc/meminfo"

# /proc/stat contains system statistics including CPU time counters
# We only care about the first line, which starts wth CPU and contains timing information
# in units of USER_HZ (typically 1/100th of a second)
PROC_STAT_PATH = "/proc/stat"

# /proc/uptime contains two numbers, system uptime and idle time
# We only care about the first
PROC_UPTIME_PATH = "/proc/uptime"

# SYSFS PATHS
# Root directory for Direct Rendering Manager devices
# Each GPU appears as a subdirectory (card0, card1)
DRM_ROOT = "/sys/class/drm"

# Root directory for hardware monitoring sensors
# Each sensor appears as hwmonX
# Each hwmon directory contains files like tempX_input and tempX_label
HWMON_ROOT = "/sys/class/hwmon"

# GPU MEMORY PATHS
# These are relative paths under each card directory in DRM_ROOT

# Current VRAM usage in bytes 
# "vis_vram" refers to memory directly accessible by the CPU
GPU_USED_VRAM_PATH = "device/mem_info_vis_vram_used"

# Total visible VRAM capacity in bytes
GPU_TOTAL_VRAM_PATH = "device/mem_info_vis_vram_total"

# TEMPERATURE SENSOR CONFIGURATION
"""
HWMON SENSOR NAMING: 
The hwmon subsystem in Linux provides a standardized interface for hardware monitoring.
Each sensor chip gets a hwmon directory with:
- A name file containing the sensor chip identifier
- Multiple tempX_label files describing what each sensor measures
- Corresponding tempX_input files with the actual temperature in millidegrees Celsius

AMD SENSORS:
AMD has their own naming conventions for their temperature sensors
- k10temp: CPU temperature sensor for AMD K10 and newer architectures 
           (Added to kernel in 2010)
- amdgpu: GPU temperature sensor for AMD Radeon graphics
"""

# CPU sensor identification 
CPU_SENSOR_NAME = "k10temp"

# Which CPU temperature to monitor
# Temperature Control is AMD's control temperature that triggers thermal throttling.
# It represents the hottest point on the CPU die and is the most relevant metric for 
# monitoring CPU thermal health.
CPU_TEMP_LABEL = "tctl"

# GPU sensor identification
GPU_SENSOR_NAME = "amdgpu"

# Which GPU temperature to monitor
# The junction is the hottest temperature measured on the GPU die
GPU_TEMP_LABEL = "junction" 