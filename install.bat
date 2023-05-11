@echo off

REM Remove the existing container if it exists
docker rm telegramm_container

REM Remove the existing image if it exists
docker rmi telegrammbot

REM Build the new image
docker build -t telegrammbot .

REM Run the new container
docker run -d --name telegramm_container telegrammbot

echo Wenn sich das Fenster geschlossen hat, kannst du den Bot benutzen!

ping -n 30 localhost > nul