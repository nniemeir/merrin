# The reported metrics appear 17 characters in to their respective rows
FIELD_TWO_COL = 17 

DEFAULT_UPDATE_INTERVAL = 1
CPU_USAGE_INTERVAL = 1

PROC_MEMINFO_PATH = "/proc/meminfo"
PROC_STAT_PATH = "/proc/stat"
PROC_UPTIME_PATH = "/proc/uptime"

DRM_ROOT = "/sys/class/drm"
HWMON_ROOT = "/sys/class/hwmon"

GPU_USED_VRAM_PATH = "device/mem_info_vis_vram_used"
GPU_TOTAL_VRAM_PATH = "device/mem_info_vis_vram_total"

CPU_SENSOR_NAME = "k10temp"
# A high Tctl is what triggers thermal throttling, as it represents the hottest point on the CPU
CPU_TEMP_LABEL = "tctl"

GPU_SENSOR_NAME = "amdgpu"
# A high junction temperature is what triggers thermal throttling, as the junction is the hottest point on the GPU
GPU_TEMP_LABEL = "junction" 