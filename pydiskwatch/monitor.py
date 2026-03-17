import psutil
from dataclasses import dataclass
from typing import List

@dataclass
class PartitionInfo:
    device: str
    mountpoint: str
    fstype: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float

def get_disk_usage() -> List[PartitionInfo]:
    partitions = []
    # all=False excludes pseudo-filesystems like /proc, /sys
    # Since we only want physical devices usually. For Windows it just skips empty drives etc.
    for part in psutil.disk_partitions(all=False):
        # Ignore cdrom, etc.
        if 'cdrom' in part.opts or part.fstype == '':
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append(PartitionInfo(
                device=part.device,
                mountpoint=part.mountpoint,
                fstype=part.fstype,
                total_gb=round(usage.total / 1e9, 2),
                used_gb=round(usage.used / 1e9, 2),
                free_gb=round(usage.free / 1e9, 2),
                percent=usage.percent,
            ))
        except PermissionError:
            continue
        except FileNotFoundError:
            # Mountpoint not found, skip
            continue
    return partitions
