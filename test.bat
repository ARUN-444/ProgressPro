@echo off
title ProgressPro Test Suite
echo ============================================================
echo Running ProgressPro Pytest Automated Test Suite...
echo ============================================================
echo.

.\.venv\Scripts\python.exe -m pytest -v
pause
