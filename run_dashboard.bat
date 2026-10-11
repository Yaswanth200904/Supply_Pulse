@echo off
echo ========================================================
echo   Launching SupplyPulse Autonomous AI Command Center
echo ========================================================
cd /d "%~dp0\.."
streamlit run supplypulse\app.py
pause
