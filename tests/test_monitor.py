from unittest.mock import patch, MagicMock
from pydiskwatch.monitor import get_disk_usage

def test_get_disk_usage_returns_list():
    mock_part = MagicMock(device='/dev/sda1', mountpoint='/', fstype='ext4', opts='rw')
    mock_usage = MagicMock(total=100e9, used=60e9, free=40e9, percent=60.0)
    
    with patch('psutil.disk_partitions', return_value=[mock_part]):
        with patch('psutil.disk_usage', return_value=mock_usage):
            result = get_disk_usage()
            assert len(result) == 1
            assert result[0].percent == 60.0
            assert result[0].device == '/dev/sda1'
            assert result[0].total_gb == 100.0

def test_get_disk_usage_ignores_cdrom():
    mock_part = MagicMock(device='/dev/cdrom', mountpoint='/mnt/cdrom', fstype='iso9660', opts='cdrom,ro')
    with patch('psutil.disk_partitions', return_value=[mock_part]):
        result = get_disk_usage()
        assert len(result) == 0

def test_get_disk_usage_permission_error():
    mock_part = MagicMock(device='/dev/sda1', mountpoint='/', fstype='ext4', opts='rw')
    with patch('psutil.disk_partitions', return_value=[mock_part]):
        with patch('psutil.disk_usage', side_effect=PermissionError):
            result = get_disk_usage()
            assert len(result) == 0
