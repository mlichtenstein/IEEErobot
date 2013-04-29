#ifndef SETTINGS_INCLUDED
#define SETTINGS_INCLUDED

// Comment out to turn on debugging.
#define NODEBUG

// BEGIN Port Setttings
#define ROBOT_SERIAL_PORT_SPEED 9600
//9600
#define ROBOT_SERIAL_PORT_ADDRESS "/dev/ttyACM0"
#define ROBOT_SERIAL_PORT_HELLO_BYTE '+'
#define ROBOT_SERIAL_PORT_SESSION_TIMEOUT 30
#define ROBOT_MAX_MESSAGE_SIZE 200
#define ROBOT_MSG_TERMINATOR ';'
#define ROBOT_MSG_START ':'
// END Port Settings

// BEGIN Message Settings
#define ROBOT_SERIAL_MESSAGE_START ':'
#define ROBOT_SERIAL_MESSAGE_STOP ';'
#define ROBOT_SERIAL_MESSAGE_CONFIRMATION 'C'
// END Message Settings

// BEGIN Time Distance Settings
#define MS_PER_FOOT 3846 //the inverse linear velocity of the robot
#define MS_PER_DEGREE 38 //the inverse angular velocity of the robot
// END Time Distance Settings

// BEGIN Scan Settings
#define ROBOT_SCAN_DELAY 30
#define ROBOT_SCAN_DATA_POINTS 50
#define ROBOT_SCAN_ANGLE 145
#define ROBOT_SCAN_IR_RANGELIM 4
// END Scan Settings

// BEGIN Services
#define ROBOT_PING_TEST 'P'
//#define ROBOT_SERVICE_CAMERA 'C'
//#define ROBOT_SERVICE_IMO 'I'
#define ROBOT_SERVICE_SCAN 'J'
#define ROBOT_SERVICE_CALIBRATE_SERVO 'M'
#define ROBOT_SERVICE_TEST_SERVO 'L'
#define ROBOT_SERVICE_ARM_SERVO 'G'
#define ROBOT_SERVICE_GO 'T'
#define ROBOT_COMMAND_TURN 'T'
#define ROBOT_COMMAND_SCOOT 'S'
#define ROBOT_CALIB_IR 'i'
#define ROBOT_WAIT_MODE 'W'
#define ROBOT_COMMAND_FORWARD 'F'
// END Services

// BEGIN Responses
#define ROBOT_RESPONSE_ERROR 'E'
#define ROBOT_RESPONSE_COMFIRM 'C'
// END Responses

// BEGIN Error
#define ROBOT_SERIAL_ERROR_BAD_MESSAGE 1
#define ROBOT_SERIAL_ERROR_NO_SERVICE 1
#define ROBOT_SERIAL_ERROR_WRONG_ARGUMENTS 1
// END Error

typedef int Number;
#ifndef TESTING
#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif
#endif
#include <Servo.h>
#endif // SETTINGS_INCLUDED

