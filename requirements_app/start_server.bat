@echo off
setlocal
cd /d C:\Apps\QRConference
call myvenv\Scripts\activate.bat

:: serwer w PRZODZIE – NSSM nad nim panuje
C:\Apps\QRConference\myvenv\Scripts\python.exe manage.py runserver 0.0.0.0:8000 --noreload

endlocal
exit /b %errorlevel%S
