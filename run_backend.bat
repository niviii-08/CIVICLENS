@echo off
echo ====================================================
echo Starting CIVICLENS TN - Flask REST API (Port 5000)
echo ====================================================
python -m flask --app backend/api/app.py run --port 5000
pause
