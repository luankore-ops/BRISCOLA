@echo off
rem Crea dist\Briscola.exe. Modifica PY se Python e' installato altrove.
set PY="C:\Program Files\Python314\python.exe"

%PY% -m pip install -r requirements.txt
%PY% -m PyInstaller --noconfirm --onefile --windowed --name Briscola --add-data "assets;assets" play.py
echo.
echo Fatto: dist\Briscola.exe
pause
