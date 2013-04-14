#if defined( ROBOT_SERVICE_ARM_SERVO ) && !defined( GUARD_ARM_HEADER )
#define GUARD_ARM_HEADER
extern int newArmTheta[];
void setupArm();
void armControl();
void magnet(char aChar);
#ifndef TESTING
#if ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif
#endif
#endif
