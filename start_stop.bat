@echo off

set container_name=telegramm_container

docker ps -q -f name=%container_name% | findstr /r /c:"[a-z0-9]*" > nul
if %errorlevel% equ 0 (
  echo Stopping container %container_name%...
  docker stop %container_name%
  echo Der Telegramm-Bot wurde beendet!
  ping -n 10 localhost > nul
) else (
  echo Starting container %container_name%...
  docker start %container_name%
  echo Der Telegramm-Bot wurde gestartet und ist nun Einsatz bereit!
  ping -n 10 localhost > nul
)

echo Done.
