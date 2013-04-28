#include "Settings.h"
#include "scan.h"

//This block defines pins for the Eye modules
Servo EyeServo[4];
//the minimum read time--used to ensure that the scan doesn't go so fast
int pos;
int deltaPos = 1;
int IRpin[] = {A0,A1,A2,A3};
int pingPin[] = {46,48,50,52};
int servoPin[] = {10,11,12,13};
#define IRMATION 'C'
// END Message Settings

void setupScan() {
    for (int i = 0; i<4; i++) {
        EyeServo[i].attach(servoPin[i]);
        EyeServo[i].write(0);
        pinMode(IRpin[i], INPUT);
    }
}
//here is a function for the Eye modules
int PingFire(int servoNum) {
    int pin = pingPin[servoNum];
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    delayMicroseconds(2);
    digitalWrite(pin, HIGH);
    delayMicroseconds(5);
    digitalWrite(pin, LOW);
    pinMode(pin, INPUT);
    return pulseIn(pin,HIGH,2000);
}
//here is a function that wraps the Savox servos
void EyeServoWrite(int servoNum, int pt) {
    int rmin;
    int rmax;
    switch (servoNum) {
        //rmin and rmax are the minimum and maximum unwrapped thetas the servos accept
        //find them with the M control char case below
    case 0:
        rmin = 10;
        rmax = 170;
        break;
    case 1:
        rmin = 15;
        rmax = 170;
        break;
    case 2:
        rmin = 20;
        rmax = 170;
        break;
    case 3:
        rmin = 35;
        rmax = 170;
        break;
    }
    if (servoNum == 1 || servoNum == 3) {
        int temp;    //swapping rmin and rmax makes 1 and 3 go counterclockwise
        temp = rmin;
        rmin = rmax;
        rmax = temp;
    }
    float wrappedTheta = float(rmin) + float(rmax - rmin)*pt/ROBOT_SCAN_DATA_POINTS;
    EyeServo[servoNum].write(int(wrappedTheta));

}
