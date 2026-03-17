import os
import shutil
from unittest.mock import patch, mock_open
from pydiskwatch.config import Config, Config, ReportConfig
from pydiskwatch.monitor import PartitionInfo
from pydiskwatch.reporter import generate_report

def test_generate_report(tmpdir):
    out_dir = str(tmpdir.mkdir("reports"))
    
    cfg = Config()
    cfg.report = ReportConfig(output_dir=out_dir, formats=['html', 'csv'])
    cfg.thresholds.disk_usage_percent = 80
    
    partitions = [PartitionInfo(device='/dev/sda1', mountpoint='/', fstype='ext4', total_gb=100.0, used_gb=50.0, free_gb=50.0, percent=50.0)]
    
    with patch('pydiskwatch.reporter.get_disk_errors', return_value=[]):
        generate_report(partitions, cfg, output_dir=out_dir)
        
    generated_files = os.listdir(out_dir)
    assert any(f.endswith('.html') for f in generated_files)
    assert any(f.endswith('.csv') for f in generated_files)
    
    # Clean up (tmpdir handles this usually but good practice)
    shutil.rmtree(out_dir, ignore_errors=True)
