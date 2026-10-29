@echo off
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

echo.
echo Откат возвращает телевизор к снимку.
echo Программы не удаляются. Сброс настроек не нужен.
echo.
echo Не нажимайте клавишу просто так. Сначала впишите адрес телевизора.
echo Пример: 192.168.50.65
echo.

if not exist "%~dp0platform-tools\adb.exe" (
  echo Не найден файл adb.exe в папке platform-tools. Ничего не сделано.
  echo.
  echo Прочитайте текст выше. Окно закроется после нажатия клавиши.
  pause
  exit /b 1
)

set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  echo Python не найден. Ничего не сделано.
  echo.
  echo Прочитайте текст выше. Окно закроется после нажатия клавиши.
  pause
  exit /b 1
)

:ask
set "TVIP="
set /p TVIP=Впишите адрес целиком и только потом нажмите Enter: 
if not defined TVIP goto ask
if "%TVIP%"=="" goto ask

echo.
echo Соединяюсь с %TVIP%. Если телевизор спросит разрешение, на пульте нажмите ОК.
echo.
%PY% откат.py --host %TVIP%
echo.
echo Если на телевизоре был вопрос, нажмите ОК и запустите Откат.bat ещё раз.
echo Когда в окне написано Готово, выключите отладку по USB.
echo Прочитайте текст выше. Окно закроется после нажатия клавиши.
pause
