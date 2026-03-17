import os
import csv
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from typing import List

from pydiskwatch.monitor import PartitionInfo
from pydiskwatch.config import Config
from pydiskwatch.log_parser import get_disk_errors

def generate_report(partitions: List[PartitionInfo], config: Config, output_dir: str = "./reports"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    display_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate thresholds alerts
    alerts = []
    for part in partitions:
        if part.percent > config.thresholds.disk_usage_percent:
            alerts.append(f"High usage on {part.mountpoint}: {part.percent}%")
        elif part.free_gb < config.thresholds.free_space_gb:
            alerts.append(f"Low free space on {part.mountpoint}: {part.free_gb} GB")
            
    log_errors = get_disk_errors()

    if "html" in config.report.formats:
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')))
        template = env.get_template('report.html')
        html_content = template.render(
             partitions=partitions,
             config=config,
             timestamp=display_time,
             alerts=alerts,
             log_errors=log_errors
        )
        html_path = os.path.join(output_dir, f'report_{timestamp_str}.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    if "csv" in config.report.formats:
        csv_path = os.path.join(output_dir, f'report_{timestamp_str}.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Device', 'Mountpoint', 'FS Type', 'Total GB', 'Used GB', 'Free GB', 'Usage %'])
            for part in partitions:
                writer.writerow([part.device, part.mountpoint, part.fstype, part.total_gb, part.used_gb, part.free_gb, part.percent])
