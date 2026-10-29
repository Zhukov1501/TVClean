@echo off
setlocal
cd /d "%~dp0"
echo Версия 3
echo.
echo Снимок. Телевизор пока не меняется.
echo Одна клавиша окно не закрывает.
echo Адрес на телевизоре: Настройки, Сеть, IP-адрес.
echo Нужна короткая строка. Пример: 192.168.50.65

set "ADB="
for /r "%~dp0" %%F in (adb.exe) do if not defined ADB set "ADB=%%F"
if defined ADB goto haveadbfile
echo.
echo Не найден файл adb.exe. Телевизор поэтому молчит.
echo Распакуйте архив так, чтобы adb.exe лежал внутри папки Телевизор.
echo Сейчас в папке лежит:
dir /b
call :hold
exit /b 1

:haveadbfile
set "TV_ADB=%ADB%"
for %%D in ("%ADB%") do set "ADBDIR=%%~dpD"
if exist "%ADBDIR%AdbWinApi.dll" goto haveadb
echo.
echo Файл adb.exe есть, но рядом нет AdbWinApi.dll.
echo Скопируйте всю папку platform-tools, не один файл adb.exe.
echo Папка с adb: %ADBDIR%
call :hold
exit /b 1

:haveadb
set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py -3"
if defined PY goto havepy
echo.
echo Python не найден. Телевизор поэтому молчит.
echo Поставьте Python с сайта python.org
echo В начале установки отметьте Add python.exe to PATH.
call :hold
exit /b 1

:havepy
:ask
set "TVIP="
set /p TVIP=Впишите адрес 192.168... и только потом нажмите Enter: 
if not defined TVIP goto ask
if "%TVIP%"=="" goto ask
echo.
echo Соединяюсь с %TVIP%. Если телевизор спросит разрешение, на пульте нажмите ОК.
echo.
%PY% оптимизация.py --host %TVIP%
echo.
echo Прочитайте текст выше. Телевизор отвечает только если здесь нет слова ошибки.
call :hold
exit /b 0

:hold
echo.
echo Окно само не закроется.
echo Чтобы закрыть его, напишите слово выход и нажмите Enter.
:holdask
set "ANS="
set /p ANS=Слово для закрытия: 
if /I not "%ANS%"=="выход" goto holdask
exit /b 0
