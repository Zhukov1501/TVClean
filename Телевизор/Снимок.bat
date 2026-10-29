@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo.
echo Снимок. Телевизор пока не меняется.
echo Адрес: Настройки, Сеть, IP-адрес.
echo Берите короткую строку с 192.168. Длинную fe80 не берите.
echo.
set /p TVIP=Вставьте адрес и нажмите Enter: 
if "%TVIP%"=="" (
  echo Адрес пустой. Закройте окно и начните снова.
  pause
  exit /b 1
)
where python >nul 2>&1
if errorlevel 1 (
  echo Python не найден. Поставьте его с python.org и отметьте Add python.exe to PATH.
  pause
  exit /b 1
)
python оптимизация.py --host %TVIP%
echo.
echo Если телевизор спросил разрешение, на пульте нажмите ОК и запустите Снимок.bat ещё раз.
pause
