@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo.
echo Сейчас выключится только реклама и встроенный очиститель.
echo Кинопоиск, Музыка, Happ, YouTube, Netflix, пульт и каналы остаются.
echo Если станет хуже, сразу запустите Откат.bat.
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
python оптимизация.py --host %TVIP% --применить
echo.
echo Теперь на телевизоре выключите отладку по USB.
pause
