@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo.
echo Откат возвращает телевизор к снимку.
echo Программы не удаляются. Сброс настроек не нужен.
echo.
set /p TVIP=Вставьте адрес телевизора и нажмите Enter: 
if "%TVIP%"=="" (
  echo Адрес пустой. Ничего не сделано.
  pause
  exit /b 1
)
where python >nul 2>&1
if errorlevel 1 (
  echo Python не найден. Поставьте его с python.org и отметьте Add python.exe to PATH.
  pause
  exit /b 1
)
python откат.py --host %TVIP%
echo.
echo Если телевизор спросил разрешение, на пульте нажмите ОК и запустите Откат.bat ещё раз.
echo Когда в окне написано Готово, выключите отладку по USB.
pause
