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
int servoPin[] = {3,4,5,6};

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
#endif

#ifdef ROBOT_SERVICE_ARM_SERVO
#define ARM_SERVOS 3
#define ARM_SERVO_ID1 5
#define ARM_SERVO_ID2 6
#define ARM_SERVO_ID3 10
/// The arm servos.
Servo R[ARM_SERVOS];
/// Initial angles for the arm.
Number initArmThetas[ ARM_SERVOS ] = { 0, 0, 0 };
/// Tracks the arm and helps control it.
Arm armManager( initArmThetas );
#endif

/// A counter for out going IDs.
int messageID = 0;

char inBoxBuffer[ 1000 ] = "";
int inBoxBuffer_newChar = 0;

void establishContact( );
bool readMessage( );

void setup() {
    #ifdef ROBOT_SERVICE_ARM_SERVO
    R[0].attach(ARM_SERVO_ID1);
    R[1].attach(ARM_SERVO_ID2);
    R[2].attach(ARM_SERVO_ID3);
    for ( int i = 0; i < ARM_SERVOS; ++i ) {
        R[ i ].write( initArmThetas[ i ] );
    }
    #endif
    #ifdef ROBOT_SERVICE_IRSENSOR_POLL
    for (int i = 0; i<2; i++) {
        myservo[i].attach(servoPin[i]); //servos attach
        myservo[i].write(0);
    }
    #endif
    Serial.begin( ROBOT_SERIAL_PORT_SPEED );
    establishContact( );
    Serial.flush();
    delay( 100 );
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
                        for (int i = 0; i<2; i++) {
                            EyeServo[i].write(pos);
                            USreading[i] = PingFire(i);  //this can be slow if we do it 4 times...might need more delicate code
                            IRreading[i] = analogRead(IRpin[i]);
                            //delay(DELAY);
                        }
                        while (millis() <= lastTime+DELAY) {} //wait for minimum read time to elapse, if nec
                        for (int i=0; i<4; i++) {
                            Serial.print( char('|'));
                            Serial.print( (pos));
                            Serial.write( ',' );
                            Serial.print( (IRreading[i] & 255));
                            Serial.write( ',' );
                            Serial.print( (IRreading[i] >> 8));
                            Serial.write( ',' );
                            Serial.print( (USreading[i] & 255));
                            Serial.write( ',' );
                            Serial.print( (USreading[i] >> 8));
                            Serial.write( ',' );
                            Serial.print( (i)); //ServoNum
                        }
                        Serial.write( ';' );
                    }
                    for (int i = 0; i<2; i++) {
                        EyeServo[i].write(0);
                    }
                }
                break;
                #endif
                #ifdef ROBOT_SERVICE_ARM_SERVO
                case ROBOT_SERVICE_ARM_SERVO: {
                    int thetas[3];
                    numOfVars = sscanf( inBoxBuffer, "%*c%*d",
                                        &( thetas[0] ), &( thetas[1] ), &( thetas[2] ) );
                    if ( numOfVars == 3 ) {
                        Serial.write( ':' );
                        Serial.write( ROBOT_RESPONSE_COMFIRM );
                        Serial.print( id );
                        Serial.write( ';' );
                        armManager.setNewTheta( millis(), result->list );
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




