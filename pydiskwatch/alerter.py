import smtplib
from email.mime.text import MIMEText
from typing import List
from plyer import notification

from pydiskwatch.monitor import PartitionInfo
from pydiskwatch.config import Config

def check_and_alert(partitions: List[PartitionInfo], config: Config, override_threshold: int = None):
    threshold = override_threshold if override_threshold is not None else config.thresholds.disk_usage_percent
    
    alerts = []
    for part in partitions:
        if part.percent >= threshold:
            alerts.append(f"Partition {part.mountpoint} ({part.device}) usage is {part.percent}% "
                          f"(Threshold: {threshold}%). Free: {part.free_gb} GB")
        elif part.free_gb < config.thresholds.free_space_gb:
            alerts.append(f"Partition {part.mountpoint} ({part.device}) free space is critically low: "
                          f"{part.free_gb} GB (Threshold: {config.thresholds.free_space_gb} GB)")
                          
    if not alerts:
        return
        
    alert_message = "\n".join(alerts)

    if config.alerts.desktop.enabled:
        try:
            notification.notify(
                title='PyDiskWatch Alert',
                message=alert_message,
                app_name='PyDiskWatch',
                timeout=10
            )
        except Exception as e:
            print(f"Failed to send desktop notification: {e}")

    if config.alerts.email.enabled:
        email_cfg = config.alerts.email
        if not email_cfg.sender or not email_cfg.receiver or not email_cfg.password:
             print("Email alerts enabled but credentials/recipients missing in config.")
             return
             
        msg = MIMEText(alert_message)
        msg['Subject'] = 'PyDiskWatch Disk Alert'
        msg['From'] = email_cfg.sender
        msg['To'] = email_cfg.receiver

        try:
            # Use smtplib.SMTP_SSL for secure connection over port 465
            if email_cfg.smtp_port == 465:
                # Need to use SMTP_SSL as per python docs for port 465
                import ssl
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(email_cfg.smtp_host, email_cfg.smtp_port, context=context) as server:
                    server.login(email_cfg.sender, email_cfg.password)
                    server.sendmail(email_cfg.sender, [email_cfg.receiver], msg.as_string())
            else:
                with smtplib.SMTP(email_cfg.smtp_host, email_cfg.smtp_port) as server:
                    server.starttls()
                    server.login(email_cfg.sender, email_cfg.password)
                    server.sendmail(email_cfg.sender, [email_cfg.receiver], msg.as_string())
                    
        except Exception as e:
            print(f"Failed to send email alert: {e}")
