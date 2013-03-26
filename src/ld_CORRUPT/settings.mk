TARGET=$(notdir $(CURDIR))
PORT=/dev/ttyACM0
AVRDUDE_PROGRAMMER=arduino
ARDUINO_BASE=/home/shared/Downloads/Arduino-0023
BOARDFILE=../../res/boards.txt
MODEL=uno
AVR_TOOLS_PATH=/usr/bin
SRCCDEF=-I../../inc -I$(ARDUINO_BASE)/libraries/Servo
