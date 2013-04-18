#include "Settings.h"
#include "go.h"


#include <math.h>

//Coordinates of wheel stems in cartesian plane with origin at center of bot
#define BODY_WIDTH 4.515625
#define BODY_LENGTH 3.6875

//Front-left servo, etc
Servo FLSERVO, FRSERVO, BLSERVO, BRSERVO;
//Pin numbers for wheel servos, motor pairs
const int LEFT_DIR1 = 25, LEFT_DIR2 = 24, RIGHT_DIR1 = 26, RIGHT_DIR2 = 27;
/*
H-BRIDGE:    LEFT_DIR1       LEFT_DIR2      RIGHT_DIR1        RIGHT_DIR2
forward          0               1               1                 0
reverse          1               0               0                 1
rotate right     0               1               0                 1
rotate left      1               0               1                 0
*/
const int LEFT_SPEED = 2, RIGHT_SPEED = 3;

void setupGo() {
    //Attach Servos
    FLSERVO.attach(30); //front left servo
    FRSERVO.attach(31); //front right servo
    BLSERVO.attach(32); //back left servo
    BRSERVO.attach(33); //back right servo
    pinMode(LEFT_DIR1, OUTPUT);
    pinMode(LEFT_DIR2, OUTPUT);
    pinMode(RIGHT_DIR1, OUTPUT);
    pinMode(RIGHT_DIR2, OUTPUT);
}
void scoot(double distance, double angle) {
    int forwardFlag = 1;
    while (angle > 180) {
        forwardFlag *=-1;
        angle -= 360;
    }
    while (angle < -180) {
        forwardFlag *=-1;
        angle += 360;
    }

    if (-90 <= angle && angle <= 90) {
        //       Serial.println("angle is: ");
        //Serial.println(angle-180);
        faceWheels(angle);
    } else if (angle > 90) {
        Serial.write("angle = \n");
        Serial.println(angle-180);
        faceWheels(angle-180);
        forwardFlag *= -1;
    } else if (angle < -90) {
        faceWheels(angle+180);
        forwardFlag *= -1;
    }
    if (forwardFlag == 1) {
        forward(distance);
    } else if (forwardFlag == -1) {
        reverse(distance);
    }
}

void go(double x, double y, double theta) {
    double angle = 180/PI*atan2(y,x);
    //Serial.println(angle);
    turn(angle);
    forward(hypot(x,y));
    double dAngle=theta-angle;
    turn(dAngle);

}
void turn(double angle) {
    //translate angle to live in [-180,180]
    if (angle<0) {
        left(abs(angle));
    } else if (angle>0) {
        right(abs(angle));
    }
}

void right(double Angle) {
    //pass a degree, will use for delay
    motorSpeed(0);
    digitalWrite(LEFT_DIR1, LOW);
    digitalWrite(LEFT_DIR2, HIGH);
    digitalWrite(RIGHT_DIR1, LOW);
    digitalWrite(RIGHT_DIR2, HIGH);
    FLSERVO.write(90+40);   //front right servo
    FRSERVO.write(90-40);   //back right servo
    BLSERVO.write(90-40);   //back left
    BRSERVO.write(90+40);   //front left
    delay(500);
    motorSpeed(255);
    delay(int(Angle*MS_PER_DEGREE));
    motorSpeed(0);
}

void left(double Angle) {
    motorSpeed(0);
    digitalWrite(LEFT_DIR1, HIGH);
    digitalWrite(LEFT_DIR2, LOW );
    digitalWrite(RIGHT_DIR1, HIGH);
    digitalWrite(RIGHT_DIR2, LOW);
    FLSERVO.write(90+40);   //set servos
    FRSERVO.write(90-40);
    BLSERVO.write(90-40);
    BRSERVO.write(90+40);
    delay(500);
    motorSpeed(255);
    delay(int(Angle*MS_PER_DEGREE));
    motorSpeed(0);
}

void forward(double feet) {
    motorSpeed(0);
    digitalWrite(LEFT_DIR1, LOW);
    digitalWrite(LEFT_DIR2, HIGH );
    digitalWrite(RIGHT_DIR1, HIGH);
    digitalWrite(RIGHT_DIR2, LOW);
    /*    FLSERVO.write(90);   //set servos
        FRSERVO.write(90);
        BLSERVO.write(90);
        BRSERVO.write(90);*/
    delay(500);
    motorSpeed(255);
    delay(int(feet*MS_PER_FOOT)); //changed so that speed is a setting
    motorSpeed(0);
}

void reverse(double feet) {
    motorSpeed(0);
    digitalWrite(LEFT_DIR1, HIGH);
    digitalWrite(LEFT_DIR2, LOW );
    digitalWrite(RIGHT_DIR1, LOW );
    digitalWrite(RIGHT_DIR2, HIGH);
    /*  FLSERVO.write(90);   //set servos
        FRSERVO.write(90);
        BLSERVO.write(90);
        BRSERVO.write(90); */
    delay(500);
    motorSpeed(255);
    delay(int(feet*MS_PER_FOOT));  //changed so that speed is a setting
    motorSpeed(0);
}


void motorSpeed(double inSpeed) {
    analogWrite(LEFT_SPEED, inSpeed);
    analogWrite(RIGHT_SPEED, inSpeed);
}

void wheelAngle(double FL_SERVO, double FR_SERVO) {
    //this function writes out the servo values
    FLSERVO.write(90-FL_SERVO);   //set servos
    FRSERVO.write(90+FR_SERVO);
    BLSERVO.write(90+FL_SERVO);
    BRSERVO.write(90-FR_SERVO);
}

void faceWheels(double angle) {
    //this function writes out the servo values
    Serial.write("Angle= ");
    Serial.print(angle);
    FLSERVO.write(angle+90);   //set servos
    FRSERVO.write(angle+90);
    BLSERVO.write(angle+90);
    BRSERVO.write(angle+90);
}

void ackSolve(float theta, double motorSpeed) {
    //Ackermann Function: Returns servo angles, and motor speeds

    double FL_Angle, FR_Angle, leftSpeed, rightSpeed, FL_SERVO, FR_SERVO, BL_SERVO, BR_SERVO;

    // turn theta into radians
    theta = theta * PI / 180;


    // find ackerman center of rotation
    float xPos = BODY_LENGTH / tan(theta);


    // set wheel angles
    FL_Angle = atan2( BODY_LENGTH, ( xPos + BODY_WIDTH ) );
    FR_Angle = atan2( BODY_LENGTH, ( xPos - BODY_WIDTH ) );


    //set motor speeds
    leftSpeed  = motorSpeed * hypot( xPos + BODY_WIDTH, BODY_LENGTH ) / hypot( xPos - BODY_WIDTH, BODY_LENGTH );
    rightSpeed = motorSpeed * hypot( xPos - BODY_WIDTH, BODY_LENGTH ) / hypot( xPos + BODY_WIDTH, BODY_LENGTH );


    //fix servo angles that are outside of their ranges, and reverse motors accordingly
    if (FL_Angle < -PI / 2) {         //Front Left wheel went too far left
        FL_Angle += PI;                  //rotate front left wheel 180 to the right
        // reverse motor here
    }
    if (FL_Angle > PI / 2) {          //Front right wheel went too far right
        FL_Angle -= PI;                  //rotate front left wheel 180 to the left
        // reverse motor here
    }
    if (FR_Angle < -PI / 2) {         //Front right wheel went too far left
        FR_Angle += PI;                  //rotate front right wheel 180 to the right
        //reverse motor here
    }
    if (FR_Angle > PI / 2) {          //Front right wheel went too far right
        FR_Angle -= PI;                  //rotate front right wheel 180 to the left
        //reverse motor here
    }

    //exit radians and convert to servo angles
    FL_SERVO=FL_Angle*180/PI+90;
    FR_SERVO=FR_Angle*180/PI+90;

    wheelAngle(FL_SERVO,FR_SERVO);
}

void ackTest() {
    int throttle=0, FL_SERVO, FR_SERVO, BL_SERVO, BR_SERVO;
    for(int angle = -90; angle < 90; angle += 1) {
        // goes from 0 degrees to 180 degrees
        ackSolve(angle, throttle); //solve ackerman
        FLSERVO.write(FL_SERVO);   //set servos
        FRSERVO.write(FR_SERVO);
        BLSERVO.write(BL_SERVO);
        BRSERVO.write(BR_SERVO);
        delay(100);                // waits 100ms
    }
    for(int angle = 90; angle>=-90; angle-=1) {
        // goes from 180 degrees to 0 degrees
        ackSolve(angle, throttle); //solve ackerman
        FLSERVO.write(FL_SERVO);   //set servos
        FRSERVO.write(FR_SERVO);
        BLSERVO.write(BL_SERVO);
        BRSERVO.write(BR_SERVO);
        delay(100);                // waits 100ms
    }
}
