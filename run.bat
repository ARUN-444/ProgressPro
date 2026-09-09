@echo off
title ProgressPro Server
echo ============================================================
echo Starting ProgressPro: Fitness Progress Analysis and Recommendation API
echo ============================================================
echo UI Dashboard:  http://127.0.0.1:8000/ui
echo Swagger Docs:  http://127.0.0.1:8000/docs
echo ReDoc:         http://127.0.0.1:8000/redoc
echo ============================================================
echo.

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
