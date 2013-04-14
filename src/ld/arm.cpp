#include "Settings.h"
#include "arm.h"


Servo R1,R2_1,R2_2,R3;
int newArmTheta[] = {0,0,0};
int oldArmTheta[] = {0,0,0};

// arm function prototypes

double convertR1(int inDegree);
double convertR2_1(int inDegree);
double convertR2_2(int inDegree);
double convertR3(int inDegree);

void setupArm() {
  //write arm to a safe angle befor bringing it online
    R1.writeMicroseconds(convertR1(90));
    R2_1.writeMicroseconds(convertR2_1(0));
    R2_2.writeMicroseconds(convertR2_1(0));
    R3.writeMicroseconds(convertR3(90));
    
    R1.attach(36);
    R2_1.attach(37);
    R2_2.attach(38);
    R3.attach(39);
    pinMode(8, OUTPUT);
    delay(1000);
}
void armControl() {
    newArmTheta[2] = 275 - newArmTheta[2];
    for(int i = 1; i <= 200; i++) {
        //Serial.write( 'i' );
        R1.writeMicroseconds((int)(convertR1(oldArmTheta[0]) + (convertR1(newArmTheta[0]) - convertR1(oldArmTheta[0]))*i/200));
        R2_1.writeMicroseconds((int)(convertR2_1(oldArmTheta[1]) + (convertR2_1(newArmTheta[1]) - convertR2_1(oldArmTheta[1]))*i/200));
        R2_2.writeMicroseconds((int)(convertR2_2(oldArmTheta[1]) + (convertR2_2(newArmTheta[1]) - convertR2_2(oldArmTheta[1]))*i/200));
        R3.writeMicroseconds((int)(convertR3(oldArmTheta[2]) + (convertR3(newArmTheta[2]) - convertR3(oldArmTheta[2]))*i/200));
        delay(10);
    }
    for(int i = 0; i < 3; i++) {
        oldArmTheta[i] = newArmTheta[i];
    }

}
void magnet(char inChar)
{
   if(inChar == 'i')
     digitalWrite(8, HIGH);
   else if(inChar == 'o')
     digitalWrite(8,LOW);
}

void magnet(char inChar)
{
  Serial.println("farts");
  if(inChar == 'i')
   digitalWrite(8, HIGH);
  else if(inChar =='o')
    digitalWrite(8, LOW);
}

// Servo angle conversion and callibration functions
// retrun [offset] + (inputDegrees/360 * [scale]
// scale = the difference between the offset and the value
// that gives a full360 of rotation
double convertR1(int inDegree) {
    return 1080 + ((double)inDegree/360 * 2350);
}
double convertR2_1(int inDegree) {
    return 1005 + ((double)inDegree/360 * 2180);
}
double convertR2_2(int inDegree) {
    return 980 + ((double)(inDegree)/360 * 2430);
}
double convertR3(int inDegree) {
    return 650 + ((double)inDegree/360 * 1800);
}
