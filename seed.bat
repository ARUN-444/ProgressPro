@echo off
title ProgressPro Database Seeder
echo ============================================================
echo Seeding ProgressPro Database with 4-Week Demo Athlete Data...
echo ============================================================
echo.

.\.venv\Scripts\python.exe scripts\seed_data.py
pause
