import sys
from unittest.mock import patch, MagicMock
from pydiskwatch.alerter import check_and_alert
from pydiskwatch.monitor import PartitionInfo
from pydiskwatch.config import Config

def test_check_and_alert_desktop_notification():
    partitions = [PartitionInfo(device='/dev/sda1', mountpoint='/', fstype='ext4', total_gb=100.0, used_gb=90.0, free_gb=10.0, percent=90.0)]
    cfg = Config()
    cfg.alerts.desktop.enabled = True
    cfg.alerts.email.enabled = False
    
    with patch('plyer.notification.notify') as mock_notify:
        check_and_alert(partitions, cfg, override_threshold=80)
        mock_notify.assert_called_once()
        args, kwargs = mock_notify.call_args
        assert 'PyDiskWatch Alert' in kwargs['title']
        assert '90.0%' in kwargs['message']

def test_check_and_alert_email_notification():
    partitions = [PartitionInfo(device='/dev/sda1', mountpoint='/', fstype='ext4', total_gb=100.0, used_gb=90.0, free_gb=10.0, percent=90.0)]
    cfg = Config()
    cfg.alerts.desktop.enabled = False
    cfg.alerts.email.enabled = True
    cfg.alerts.email.sender = 'test@example.com'
    cfg.alerts.email.receiver = 'recv@example.com'
    cfg.alerts.email.password = 'pass'
    cfg.alerts.email.smtp_port = 587
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        check_and_alert(partitions, cfg, override_threshold=80)
        
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'pass')
        mock_server.sendmail.assert_called_once()
