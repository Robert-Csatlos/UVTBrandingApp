@echo off
echo Starting the virtual environment and FastAPI server...

call venv\Scripts\activate
fastapi dev main.py
pause