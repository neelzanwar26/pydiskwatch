import yaml
from dataclasses import dataclass, field
from typing import List
import os

@dataclass
class ThresholdsConfig:
    disk_usage_percent: int = 80
    free_space_gb: int = 5

@dataclass
class EmailConfig:
    enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    sender: str = ""
    receiver: str = ""
    password: str = ""

@dataclass
class DesktopConfig:
    enabled: bool = True

@dataclass
class AlertsConfig:
    email: EmailConfig = field(default_factory=EmailConfig)
    desktop: DesktopConfig = field(default_factory=DesktopConfig)

@dataclass
class ReportConfig:
    output_dir: str = "./reports"
    formats: List[str] = field(default_factory=lambda: ["html", "csv"])

@dataclass
class Config:
    thresholds: ThresholdsConfig = field(default_factory=ThresholdsConfig)
    alerts: AlertsConfig = field(default_factory=AlertsConfig)
    report: ReportConfig = field(default_factory=ReportConfig)

def load_config(path: str = "config.yaml") -> Config:
    """Loads and validates configuration from YAML"""
    cfg = Config()
    if not os.path.exists(path):
        return cfg

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        return cfg

    if "thresholds" in data:
        cfg.thresholds = ThresholdsConfig(**data.get("thresholds", {}))
    
    if "alerts" in data:
        alerts_data = data["alerts"]
        email_data = alerts_data.get("email", {})
        desktop_data = alerts_data.get("desktop", {})
        
        # Override password with env var if available
        env_pass = os.environ.get("PDISKWATCH_PASS")
        if env_pass:
            email_data["password"] = env_pass
            
        cfg.alerts.email = EmailConfig(**email_data)
        cfg.alerts.desktop = DesktopConfig(**desktop_data)
        
    if "report" in data:
        cfg.report = ReportConfig(**data["report"])

    return cfg
