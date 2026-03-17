import argparse
from rich.console import Console
from rich.table import Table

from pydiskwatch.config import load_config
from pydiskwatch.monitor import get_disk_usage
from pydiskwatch.reporter import generate_report
from pydiskwatch.alerter import check_and_alert
from pydiskwatch.log_parser import get_disk_errors

console = Console()

def main():
    parser = argparse.ArgumentParser(prog='pydiskwatch',
        description='Disk health monitor & report generator')
    parser.add_argument('--config', default='config.yaml', help='Path to configuration YAML file')
    
    sub = parser.add_subparsers(dest='command')
    
    # pydiskwatch monitor [--threshold 80] [--alert]
    mon = sub.add_parser('monitor', help='Show live disk usage')
    mon.add_argument('--threshold', type=int, help='Override threshold from config for disk usage %')
    mon.add_argument('--alert', action='store_true', help='Trigger alerts if thresholds are exceeded')
    
    # pydiskwatch report [--out ./reports]
    rep = sub.add_parser('report', help='Generate HTML + CSV report')
    rep.add_argument('--out', help='Output directory for reports')
    
    # pydiskwatch log-scan [--file /var/log/custom.log]
    log = sub.add_parser('log-scan', help='Scan logs for storage errors')
    log.add_argument('--file', help='Path to custom log file (Linux only)')
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    if args.command == 'monitor':
        data = get_disk_usage()
        
        table = Table(title="Live Disk Usage")
        table.add_column("Device", justify="left", style="cyan", no_wrap=True)
        table.add_column("Mountpoint", justify="left", style="green")
        table.add_column("FS Type", justify="left")
        table.add_column("Total", justify="right")
        table.add_column("Used", justify="right")
        table.add_column("Free", justify="right")
        table.add_column("Usage %", justify="right")
        
        threshold = args.threshold if args.threshold else config.thresholds.disk_usage_percent
        
        for p in data:
            style = "red bold" if p.percent >= threshold else "yellow" if p.free_gb < config.thresholds.free_space_gb else ""
            table.add_row(
                p.device, p.mountpoint, p.fstype,
                f"{p.total_gb} GB", f"{p.used_gb} GB", f"{p.free_gb} GB",
                f"[{style}]{p.percent}%[/{style}]" if style else f"{p.percent}%"
            )
            
        console.print(table)
        
        if args.alert:
            check_and_alert(data, config, args.threshold)
            console.print("[green]Alert checking finished.[/green]")
            
    elif args.command == 'report':
        data = get_disk_usage()
        out_dir = args.out if args.out else config.report.output_dir
        generate_report(data, config, output_dir=out_dir)
        console.print(f"[green]Report generated successfully in {out_dir}/[/green]")
        
    elif args.command == 'log-scan':
        errors = get_disk_errors(args.file)
        if not errors:
           console.print("[green]No disk storage errors found in system logs.[/green]")
        else:
           table = Table(title="Storage Errors")
           table.add_column("Timestamp", style="dim")
           table.add_column("Level", style="red bold")
           table.add_column("Message")
           for e in errors:
               table.add_row(e.timestamp, e.level, e.message)
           console.print(table)
           
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
