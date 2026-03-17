from unittest.mock import patch, mock_open
import pydiskwatch.log_parser as parser

def test_parse_syslog_linux():
    mock_log_data = "Jan  1 10:00:00 kernel: [123.45] I/O error, dev sda, sector 1234\nJan  1 10:01:00 systemd: Started session."
    with patch('builtins.open', mock_open(read_data=mock_log_data)):
        entries = parser.parse_syslog()
        assert len(entries) == 1
        assert entries[0].level == 'ERROR'
        assert 'I/O error' in entries[0].message
        assert entries[0].timestamp == 'Jan 1 10:00:00'

@patch('subprocess.run')
def test_parse_windows_eventlog(mock_run):
    mock_stdout = "  Date: 2023-01-01T10:00:00\n  Description: The device has a bad block.\n\r\n\r\nEvent["
    mock_run.return_value.stdout = mock_stdout
    entries = parser.parse_windows_eventlog()
    
    assert len(entries) == 1
    assert '2023-01-01T10:00:00' in entries[0].timestamp
    assert 'The device has a bad block' in entries[0].message

@patch('pydiskwatch.log_parser.is_windows', return_value=True)
@patch('pydiskwatch.log_parser.parse_windows_eventlog')
def test_get_disk_errors_windows(mock_parse_win, mock_is_win):
    parser.get_disk_errors()
    mock_parse_win.assert_called_once()

@patch('pydiskwatch.log_parser.is_windows', return_value=False)
@patch('pydiskwatch.log_parser.parse_syslog')
def test_get_disk_errors_linux(mock_parse_sys, mock_is_win):
    parser.get_disk_errors()
    mock_parse_sys.assert_called_once()
