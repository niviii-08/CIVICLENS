@echo off
echo ==========================================================
echo Starting CIVICLENS TN Platform (Backend + Next.js Frontend)
echo ==========================================================
start "CivicLens Flask API" cmd /k "python -m flask --app backend/api/app.py run --port 5000"
timeout /t 3 /nobreak >nul
start "CivicLens Next.js" cmd /k "cd frontend && npm run dev"
echo.
echo ==========================================================
echo CivicLens TN is launching!
echo Backend:  http://127.0.0.1:5000/
echo Frontend: http://localhost:3000/
echo ==========================================================
