#include "Settings.h"
#ifndef TESTING
    #if ARDUINO >= 100
        #include "Arduino.h"
    #else
        #include "WProgram.h"
    #endif
#endif
#include <Servo.h>

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
}

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
                    #ifdef ROBOT_SERVICE_WHEEL_SPEED
                case ROBOT_SERVICE_WHEEL_SPEED: {
                    Serial.write( ":C" );
                    Serial.print( id );
                    Serial.write( ';' );
                }
                break;
                #endif
                #ifdef ROBOT_SERVICE_WHEEL_ANGLE
                case ROBOT_SERVICE_WHEEL_ANGLE: {
                    Serial.write( ":C" );
                    Serial.print( id );
                    Serial.write( ';' );
                }
                break;
                #endif
                #ifdef ROBOT_SERVICE_WHEEL_ENCODER
                case ROBOT_SERVICE_WHEEL_ENCODER: {
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

#endif'
