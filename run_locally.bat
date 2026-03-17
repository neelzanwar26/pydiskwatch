@echo off
echo ==============================================
echo       PyDiskWatch - Local Runner Script
echo ==============================================
echo.

echo [1] Monitoring Disk Health...
call pydiskwatch monitor

echo.
echo [2] Generating Report...
call pydiskwatch report --out ./reports

echo.
echo [3] Scanning Logs for Errors...
call pydiskwatch log-scan

echo.
echo ==============================================
echo PyDiskWatch execution completed successfully!
echo Reports are available in the ./reports folder.
echo ==============================================
pause
