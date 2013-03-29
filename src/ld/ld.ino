#include "Settings.h"
#ifndef TESTING
    #if ARDUINO >= 100
        #include "Arduino.h"
    #else
        #include "WProgram.h"
    #endif
#endif
#include <Servo.h>

#ifdef ROBOT_SERVICE_GO
#include <math.h>

//Coordinates of wheel stems in cartesian plane with origin at center of bot
#define BODY_WIDTH 4.515625
#define BODY_LENGTH 3.6875

//Front-left servo, etc
Servo FLSERVO, FRSERVO, BLSERVO, BRSERVO;
//Pin numbers for wheel servos, motor pairs
const int LEFT_DIR1 = 22, LEFT_DIR2 = 23, RIGHT_DIR1 = 24, RIGHT_DIR2 = 25;
/*
H-BRIDGE:    LEFT_DIR1       LEFT_DIR2      RIGHT_DIR1        RIGHT_DIR2
forward          0               1               1                 0
reverse          1               0               0                 1
rotate right     0               1               0                 1
rotate left      1               0               1                 0
*/
const int LEFT_SPEED = 2, RIGHT_SPEED = 3;
#endif

#ifdef ROBOT_SERVICE_SCAN

//This block defines pins for the Eye modules
Servo EyeServo[4];
int DELAY = 55;
int pos;
int deltaPos = 1;
int IRpin[] = {A0,A1,A2,A3};
int pingPin[] = {30,31,32,33};
int servoPin[] = {10,11,12,13};

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
    return pulseIn(pin,HIGH,20000);
}
//here is a function that wraps the Savox servos
void EyeServoWrite(int servoNum, float theta) {
    int rmin; int rmax;
    switch (servoNum) {
      //rmin and rmax are the minimum and maximum unwrapped thetas the servos accept
      //find them with the M control char case below
      case 0: case 1: rmin = 15; rmax = 170; break;
      case 2: rmin = 25; rmax = 160; break;
      case 3: rmin = 20; rmax = 170; break;
    }
      float wrappedTheta = float(rmin) + float(rmax - rmin)*theta/ROBOT_SCAN_ANGLE;
    EyeServo[servoNum].write(int(wrappedTheta));
    
}
#endif

#ifdef ROBOT_SERVICE_ARM_SERVO
Servo R1,R2_1,R2_2,R3;
int newArmTheta[] = {0,0,0};
int oldArmTheta[] = {0,0,0};
#endif

/// A counter for out going IDs.
int messageID = 0;

char inBoxBuffer[ 1000 ] = "";
int inBoxBuffer_newChar = 0;

void establishContact( );
bool readMessage( );
#ifdef ROBOT_SERVICE_ARM_SERVO
// arm function prototypes
void armControl();
double convertR1(int inDegree);
double convertR2_1(int inDegree);
double convertR2_2(int inDegree);
double convertR3(int inDegree);
#endif

void setup() {
    #ifdef ROBOT_SERVICE_SCAN
    for (int i = 0; i<4; i++) {
        EyeServo[i].attach(servoPin[i]);
        EyeServo[i].write(0);
        pinMode(IRpin[i], INPUT);
    }
    #endif
    Serial.begin( ROBOT_SERIAL_PORT_SPEED );
    establishContact( );
    Serial.flush();
    delay( 100 );
    
    //le arm setup
    #ifdef ROBOT_SERVICE_ARM_SERVO
    R1.attach(3);
    R2_1.attach(5);
    R2_2.attach(6);
    R3.attach(10);
    pinMode(8, OUTPUT);
    #endif
    #ifdef ROBOT_SERVICE_GO
    //Attach Servos
    Serial.begin(9600);
    FLSERVO.attach(50); //front left servo
    FRSERVO.attach(51); //front right servo
    BLSERVO.attach(52); //back left servo
    BRSERVO.attach(53); //back right servo
    pinMode(LEFT_DIR1, OUTPUT);
    pinMode(LEFT_DIR2, OUTPUT);
    pinMode(RIGHT_DIR1, OUTPUT);
    pinMode(RIGHT_DIR2, OUTPUT);
    #endif
}

/* Go Example
void loop() 
{ 
        //go(0,1,0);go(2,0,0);
        forward(3); reverse(3);turn(90);turn(-90);scoot(10,45);
        while(1){int i = 0;}
}
*/

void loop() {
    if ( Serial.available() > 0 ) {
        if ( readMessage( ) ) {
            char type;
            int id;
            int numOfVars = sscanf( inBoxBuffer, "%c%d", &type, &id );
            if ( numOfVars == 2 ) {
                switch ( type ) {
/*  The following are where you paste your arduino code.  Make sure an entry in Settings.h corresponds to your case.
Your response message should take the form ":[char],[id],[payload];"
*/                  
                
                    #ifdef ROBOT_PING_TEST
                    case ROBOT_PING_TEST: {
                    Serial.write( ":P," );
                    Serial.print( id );
                    Serial.print(",PONG");
                    Serial.write( ';' );
                }
                break;
                #endif
                case 'M': {  //this block is used for calibrating savox servos
                    Serial.write( ":M" );
                    Serial.print( id );
                    Serial.write( ';' );
                    for (int i=0; i<4; i++){
                      EyeServo[i].write(id);
                    }
                }
                break;
                case 'L': {  //this block is used for testing the calibration of savox servos
                    Serial.write( ":L" );
                    Serial.print( id );
                    Serial.write( ';' );
                    for (int i=0; i<4; i++){
                      EyeServoWrite(i, id);
                    }
                    
                }
                break;
                #ifdef ROBOT_SERVICE_GO
                case ROBOT_SERVICE_GO: {
                    Serial.write( ":C" );
                    Serial.print( id );
                    Serial.write( ';' );
                }
                break;
                #endif
                #ifdef ROBOT_SERVICE_SCAN
                case ROBOT_SERVICE_SCAN: {
                    Serial.write( ":J," );
                    Serial.print( id );
                    Serial.write( ","); 
                    int pos;
                    #define DELAY 52 //the minimum read time--used to ensure that the scan doesn't go so fast
                    float deltaTheta = ROBOT_SCAN_ANGLE/(ROBOT_SCAN_DATA_POINTS-1);
                    for (pos = 0; pos <= ROBOT_SCAN_DATA_POINTS; pos += 1) {
                        unsigned int USreading[ROBOT_SCAN_DATA_POINTS];  //each eye's US reading in usec
                        unsigned int IRreading[ROBOT_SCAN_DATA_POINTS];  //each eye's US reading in 5/1024 v
                        unsigned long lastTime = millis();  //used to establish a minimum read time
                        for (int i = 0; i<4; i++) {
                            EyeServoWrite(i,pos);
                            USreading[i] = PingFire(i);  //this can be slow if we do it 4 times...might need more delicate code
                            IRreading[i] = analogRead(IRpin[i]);
                            //delay(DELAY);
                        }
                        while (millis() <= lastTime+DELAY) {} //wait for minimum read time to elapse, if nec
                        for (int i=0; i<4; i++) {
                            Serial.print( char('|'));
                            Serial.print( (i)); //EyeNum
                            Serial.write( ',' );
                            Serial.print( (pos)); //DataPointNum
                            Serial.write( ',' );
                            Serial.print( (IRreading[i] & 255)); //IRlsb
                            Serial.write( ',' );
                            Serial.print( (IRreading[i] >> 8));  //IRmsb
                            Serial.write( ',' );
                            Serial.print( (USreading[i] & 255)); //USlsb
                            Serial.write( ',' );
                            Serial.print( (USreading[i] >> 8));  //USlsb
                        }
                    }
                    Serial.write( ';' );
                    for (int i = 0; i<4; i++) {
                      EyeServoWrite(i,0);
                      //                      EyeServo[i].write(0);
                    }
                }
                break;
                #endif
                #ifdef ROBOT_SERVICE_ARM_SERVO
                case ROBOT_SERVICE_ARM_SERVO: {
                    numOfVars = sscanf( inBoxBuffer, "%*c%*d,%d,%d,%d",
                                        &( newArmTheta[0] ), &( newArmTheta[1] ), &( newArmTheta[2] ) );
                    if ( numOfVars == 3 ) {
                        Serial.write( ':' );
                        Serial.write( ROBOT_RESPONSE_COMFIRM );
                        Serial.print( id );
                        Serial.write( ';' );
                        armControl();
                    } else {
                        Serial.write( ':' );
                        Serial.write( ROBOT_RESPONSE_ERROR );
                        Serial.print( ROBOT_SERIAL_ERROR_WRONG_ARGUMENTS );
                        Serial.write( "Error: Wrong number of arguments. Message was\"" );
                        Serial.write( inBoxBuffer );
                        Serial.write( "\";" );
                    }

                }
                break;
                #endif
                default: {
                    Serial.write( ':' );
                    Serial.write( ROBOT_RESPONSE_ERROR );
                    Serial.print( ROBOT_SERIAL_ERROR_NO_SERVICE );
                    Serial.write( "Error: No such service. Message was\"" );
                    Serial.write( inBoxBuffer );
                    Serial.write( "\";" );

                }
                }
            } else {
                Serial.write( ':' );
                Serial.write( ROBOT_RESPONSE_ERROR );
                Serial.print( ROBOT_SERIAL_ERROR_BAD_MESSAGE );
                Serial.write( "Error: Bad message. Message was\"" );
                Serial.write( inBoxBuffer );
                Serial.write( "\";" );
            }
        }
    }
    #ifdef HAS_ARM_SERVO
    if ( armManager.inMove() ) {
        for (int i = 0; i < ARM_SERVOS; ++i ) {
            int theta = armManager.currentTheta[ i ];
            if ( armManager.move( i, millis(), &theta ) ) {
                R[ i ].write( theta );
            }
        }
    }
    #endif
    delay( 150 );
}

/**
 * Reads the bytes from the serial buffer and returns true
 *  when a full message is received in full.
 *
 * @param serial can take the "Serial" object.
 * @param outMessage is used to accumulate bytes from the buffer.
 *
 * @return TRUE if a message is received or FALSE otherwise.
 */
bool readMessage( ) {
    char chr;
    static bool foundMessage = false;
    while ( Serial.available() > 0 ) {
        chr = Serial.read();
        if ( chr == ROBOT_SERIAL_MESSAGE_START ) {
            foundMessage = true;
            inBoxBuffer_newChar = 0;
        } else if ( chr == ROBOT_SERIAL_MESSAGE_STOP ) {
            if ( inBoxBuffer_newChar != 0 ) {
                inBoxBuffer[ inBoxBuffer_newChar ] = '\0';
                return true;
            }
            foundMessage = false;
        } else if ( foundMessage )
            inBoxBuffer[ inBoxBuffer_newChar++ ] = chr;
    }
    inBoxBuffer[ inBoxBuffer_newChar ] = '\0';
    return false;
}

/**
 * Waits for a greeting then returns a greeting. This
 *  function could never terminate if a byte is not
 *  received.
 *
 * Preconditions:
 * -Serial.begin() has been called successfully.
 *
 * @param serial can take the "Serial" object.
 */
void establishContact( ) {
    while ( Serial.available() <= 0 ) {
        delay( 300 );
    }
    // Write back one char.
    Serial.write( Serial.read() );
}

#ifdef ROBOT_SERVICE_ARM_SERVO
void armControl()
{
  newArmTheta[2] = 280 - newArmTheta[2];
  for(int i = 1; i <= 200; i++)
  {
     R1.writeMicroseconds((int)(convertR1(oldArmTheta[0]) + (convertR1(newArmTheta[0]) - convertR1(oldArmTheta[0]))*i/200));
     R2_1.writeMicroseconds((int)(convertR2_1(oldArmTheta[1]) + (convertR2_1(newArmTheta[1]) - convertR2_1(oldArmTheta[1]))*i/200));
     R2_2.writeMicroseconds((int)(convertR2_2(oldArmTheta[1]) + (convertR2_2(newArmTheta[1]) - convertR2_2(oldArmTheta[1]))*i/200));
     R3.writeMicroseconds((int)(convertR3(oldArmTheta[2]) + (convertR3(newArmTheta[2]) - convertR3(oldArmTheta[2]))*i/200));
     delay(10);
  }
  for(int i = 0; i < 3; i++)
  {
    oldArmTheta[i] = newArmTheta[i];
  }
  
}

// Servo angle conversion and callibration functions
// retrun [offset] + (inputDegrees/360 * [scale]
// scale = the difference between the offset and the value
// that gives a full360 of rotation
double convertR1(int inDegree)
{
  return 950 + ((double)inDegree/360 * 2440);
}
double convertR2_1(int inDegree)
{
  return 1040 + ((double)inDegree/360 * 2010);
}
double convertR2_2(int inDegree)
{
  return 1030 + ((double)(inDegree)/360 * 2300);
}
double convertR3(int inDegree)
{
  return 650 + ((double)inDegree/360 * 1800);
}

#endif
void scoot(double distance, int angle)
{
  forwardFlag = 1;
  while (angle > 180)
    {
      forwardFlag *=-1;
      angle -= 360;
    }
  while (angle < -180)
    {
      forwardFlag *=-1;
      angle += 360;
    }
  faceWheels(angle);
  if (forwardFlag == 1)
  {
    forward(distance);
  }
  else if (forwardFlag == -1)
  {
    reverse(distance);
  }
}

void go(double x, double y, int theta)
{
	int angle = 180/PI*atan2(y,x);
        //Serial.println(angle);
	turn(angle);
	forward(hypot(x,y));
	int dAngle=theta-angle;
	turn(dAngle);
	
}
void turn(int angle){
  //translate angle to live in [-180,180]
  while (angle > 180)
    {angle -= 360;}
  while (angle < -180)
    {angle += 360;}
	if (angle<0)
	{
		left(abs(angle));
	}
	else if (angle>0)
	{
		right(abs(angle));
	}
}


void right(int Angle)
{//pass a degree, will use for delay
        motorSpeed(0);
    digitalWrite(LEFT_DIR1, LOW);
		digitalWrite(LEFT_DIR2, HIGH);
		digitalWrite(RIGHT_DIR1, LOW);
		digitalWrite(RIGHT_DIR2, HIGH);
        FLSERVO.write(90-40);   //front right servo
        FRSERVO.write(90+40);   //back right servo
        BLSERVO.write(90-40);   //back left
        BRSERVO.write(90+40);   //front left
        delay(500);
        motorSpeed(255);
        delay(int(Angle/33.75*1000));
        motorSpeed(0);
}

void left(int Angle)
{
        motorSpeed(0);
                digitalWrite(LEFT_DIR1, HIGH);
		digitalWrite(LEFT_DIR2, LOW );
		digitalWrite(RIGHT_DIR1, HIGH);
		digitalWrite(RIGHT_DIR2, LOW);
        FLSERVO.write(90-40);   //set servos
        FRSERVO.write(90+40);
        BLSERVO.write(90-40);
        BRSERVO.write(90+40);
        delay(500);
        motorSpeed(255);
        delay(int(Angle/33.75*1000));
        motorSpeed(0);
}

void forward(int feet)
{
		motorSpeed(0);
		digitalWrite(LEFT_DIR1, LOW);
		digitalWrite(LEFT_DIR2, HIGH );
		digitalWrite(RIGHT_DIR1, HIGH);
		digitalWrite(RIGHT_DIR2, LOW);
        FLSERVO.write(90);   //set servos
        FRSERVO.write(90);
        BLSERVO.write(90);
        BRSERVO.write(90);
		delay(500);
		motorSpeed(255);
        delay(int(feet/.294*1000));
        motorSpeed(0);
}

void reverse(int feet)
{
		motorSpeed(0);
		digitalWrite(LEFT_DIR1, HIGH);
		digitalWrite(LEFT_DIR2, LOW );
		digitalWrite(RIGHT_DIR1, LOW );
		digitalWrite(RIGHT_DIR2, HIGH);
        FLSERVO.write(90);   //set servos
        FRSERVO.write(90);
        BLSERVO.write(90);
        BRSERVO.write(90);
		delay(500);
		motorSpeed(255);
        delay(int(feet/.294*1000));
        motorSpeed(0);
}


void motorSpeed(int inSpeed)
{
	analogWrite(LEFT_SPEED, inSpeed);
	analogWrite(RIGHT_SPEED, inSpeed);
}

void wheelAngle(int FL_SERVO, int FR_SERVO)
{ //this function writes out the servo values
  FLSERVO.write(FL_SERVO);   //set servos
  FRSERVO.write(FR_SERVO);
  BLSERVO.write(90-FL_SERVO);
  BRSERVO.write(90-FR_SERVO); 
}

void faceWheels(int angle)
{ //this function writes out the servo values
  FLSERVO.write(angle);   //set servos
  FRSERVO.write(angle);
  BLSERVO.write(angle);
  BRSERVO.write(angle); 
}

void ackSolve(float theta, double motorSpeed)
{ //Ackermann Function: Returns servo angles, and motor speeds

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
      if (FL_Angle < -PI / 2)           //Front Left wheel went too far left
      {FL_Angle += PI;                  //rotate front left wheel 180 to the right
       // reverse motor here
      }
      if (FL_Angle > PI / 2)            //Front right wheel went too far right
      {FL_Angle -= PI;                  //rotate front left wheel 180 to the left
        // reverse motor here
      }
      if (FR_Angle < -PI / 2)           //Front right wheel went too far left
      {FR_Angle += PI;                  //rotate front right wheel 180 to the right
        //reverse motor here
      }
      if (FR_Angle > PI / 2)            //Front right wheel went too far right
      {FR_Angle -= PI;                  //rotate front right wheel 180 to the left
        //reverse motor here
      } 
            
      //exit radians and convert to servo angles
      FL_SERVO=FL_Angle*180/PI+90;
      FR_SERVO=FR_Angle*180/PI+90;
      
	  wheelAngle(FL_SERVO,FR_SERVO);
}

void ackTest()
{
  int throttle=0, FL_SERVO, FR_SERVO, BL_SERVO, BR_SERVO;
  for(int angle = -90; angle < 90; angle += 1)  
  {// goes from 0 degrees to 180 degrees        
  ackSolve(angle, throttle); //solve ackerman
  FLSERVO.write(FL_SERVO);   //set servos
  FRSERVO.write(FR_SERVO);
  BLSERVO.write(BL_SERVO);
  BRSERVO.write(BR_SERVO);           
  delay(100);                // waits 100ms
  } 
  for(int angle = 90; angle>=-90; angle-=1)
  {// goes from 180 degrees to 0 degrees 
  ackSolve(angle, throttle); //solve ackerman
  FLSERVO.write(FL_SERVO);   //set servos
  FRSERVO.write(FR_SERVO);
  BLSERVO.write(BL_SERVO);
  BRSERVO.write(BR_SERVO);           
  delay(100);                // waits 100ms
  } 
}
