import platform
from rich.console import Console

console = Console()

def format_bytes(bytes_num: float) -> str:
    """Formats bytes to a human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.2f} PB"

def is_windows() -> bool:
    """Checks if current platform is Windows"""
    return platform.system().lower() == 'windows'

def is_linux() -> bool:
    """Checks if current platform is Linux"""
    return platform.system().lower() == 'linux'
