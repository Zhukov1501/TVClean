@echo off
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

echo.
echo Сейчас выключится только реклама и встроенный очиститель.
echo Кинопоиск, Музыка, Happ, YouTube, Netflix, пульт и каналы остаются.
echo Если станет хуже, сразу запустите Откат.bat.
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
  echo Поставьте его с сайта python.org и отметьте Add python.exe to PATH.
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
echo Соединяюсь с %TVIP%.
echo.
%PY% оптимизация.py --host %TVIP% --применить
echo.
echo Если всё прошло хорошо, на телевизоре выключите отладку по USB.
echo Прочитайте текст выше. Окно закроется после нажатия клавиши.
pause
