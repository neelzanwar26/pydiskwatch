import re
import platform
import subprocess
from dataclasses import dataclass
from typing import List

from pydiskwatch.utils import is_windows

# Case-insensitive patterns to search for
STORAGE_PATTERNS = [
    r'I/O error', r'disk full', r'No space left',
    r'failed to mount', r'read-only file system',
    r'disk error', r'controller error'
]

@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str

def parse_syslog(path='/var/log/syslog') -> List[LogEntry]:
    """Parse standard syslog file on Linux"""
    entries = []
    pattern = re.compile('|'.join(STORAGE_PATTERNS), re.IGNORECASE)
    try:
        with open(path, 'r', errors='replace') as f:
            for line in f:
                if pattern.search(line):
                    parts = line.split(None, 3)
                    ts = ' '.join(parts[:3]) if len(parts) >= 3 else ''
                    entries.append(LogEntry(timestamp=ts,
                        level='ERROR', message=line.strip()))
    except (FileNotFoundError, PermissionError):
        # Log file not found or permission denied, try journalctl
        try:
            cmd = ['journalctl', '-p', 'err', '--no-pager']
            result = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
            for line in result.stdout.splitlines():
                if pattern.search(line):
                    parts = line.split(None, 3)
                    ts = ' '.join(parts[:3]) if len(parts) >= 3 else ''
                    entries.append(LogEntry(timestamp=ts,
                        level='ERROR', message=line.strip()))
        except FileNotFoundError:
            pass # journalctl not found
            
    return entries

def parse_windows_eventlog() -> List[LogEntry]:
    """Parse Windows Event Log for disk errors using wevtutil"""
    entries = []
    # Event IDs related to disk errors:
    # System log:
    # 7: The device has a bad block.
    # 11: The driver detected a controller error.
    # 15: The device is not ready for access yet.
    # 51: An error was detected on device during a paging operation.
    # 153: The IO operation was retried.
    query = "Event/System[Provider[@Name='disk']] and (Event/System/EventID=7 or Event/System/EventID=11 or Event/System/EventID=32 or Event/System/EventID=51 or Event/System/EventID=153)"
    
    cmd = ['wevtutil', 'qe', 'System', '/q:' + query, '/f:text', '/rd:true', '/c:50']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
        output = result.stdout.strip()
        if output:
            blocks = output.split('\r\n\r\nEvent[')
            for block in blocks:
                if not block.strip(): continue
                lines = block.split('\n')
                ts = "Unknown"
                msg = line = ""
                for l in lines:
                    line_stripped = l.strip()
                    if line_stripped.startswith('Date:'):
                        ts = line_stripped.replace('Date:', '').strip()
                    elif line_stripped.startswith('Description:'):
                        msg = line_stripped.replace('Description:', '').strip()
                    elif line_stripped.startswith('Message:'):
                         msg = line_stripped.replace('Message:', '').strip()
                if not msg and lines:
                     # try to catch everything below first few lines
                     msg = " ".join([m.strip() for m in lines if m.strip() and not m.startswith('  ')])
                entries.append(LogEntry(timestamp=ts, level='ERROR', message=msg or block.strip()[:100]))
    except Exception as e:
        entries.append(LogEntry(timestamp='', level='ERROR', message=f"Failed to query Windows Event Log: {e}"))
    return entries

def get_disk_errors(path: str = None) -> List[LogEntry]:
    """Get disk errors from OS logs"""
    if is_windows():
        return parse_windows_eventlog()
    else:
         if path:
             return parse_syslog(path)
         else:
             return parse_syslog()
