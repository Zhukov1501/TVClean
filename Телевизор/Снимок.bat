@echo off
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

echo.
echo Окно должно остаться открытым. Телевизор пока не меняется.
echo Не нажимайте клавишу просто так. От пустого нажатия окно закрывается,
echo а на телевизоре ничего не появляется.
echo.
echo Адрес смотрите на телевизоре: Настройки, Сеть, IP-адрес.
echo Нужна короткая строка. Она начинается с 192.168
echo Пример: 192.168.50.65
echo.

if not exist "%~dp0platform-tools\adb.exe" (
  echo Не найден файл adb.exe
  echo Его место: %~dp0platform-tools\adb.exe
  echo Распакуйте архив platform-tools внутрь папки Телевизор.
  echo.
  echo Прочитайте текст выше. Окно закроется после нажатия клавиши.
  pause
  exit /b 1
)

set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  echo Python не найден.
  echo Поставьте его с сайта python.org
  echo В начале установки отметьте Add python.exe to PATH.
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
%PY% оптимизация.py --host %TVIP%
echo.
echo Если на телевизоре был вопрос, нажмите ОК и запустите Снимок.bat ещё раз.
echo Прочитайте текст выше. Окно закроется после нажатия клавиши.
pause
