#include "Settings.h"

#include "go.h"
#include "scan.h"
#include "arm.h"

#include <Servo.h>

/// A counter for out going IDs.
int messageID = 0;

char inBoxBuffer[ 1000 ] = "";
int inBoxBuffer_newChar = 0;

void establishContact( );
bool readMessage( );

void setup() {
    #ifdef ROBOT_WAIT_MODE
    #define startButton 12
    pinMode(startButton, INPUT);
    digitalWrite(startButton, HIGH);
    #endif
    #ifdef ROBOT_SERVICE_SCAN
    setupScan();
    #endif
    Serial.begin( ROBOT_SERIAL_PORT_SPEED );
    establishContact( );
    Serial.flush();
    delay( 100 );

    //le arm setup
    #ifdef ROBOT_SERVICE_ARM_SERVO
    setupArm();
    #endif
    #ifdef ROBOT_SERVICE_GO
    setupGo();
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
                    Serial.write(",PONG");
                    Serial.write( ';' );
                    Serial.write( ":C," );
                    Serial.print( id );
                    Serial.write( ';' );
                }
                break;
#endif
                //this block tests sending doubles to ard.
                case 'd': {
                    Serial.write(":d,");
                    Serial.print(id);
                    Serial.write(",");
                    int myDouble;
                    char spoil;
                    int numOfVars = sscanf( inBoxBuffer, "%c%d", &spoil, &myDouble );
                    Serial.print(myDouble);
                    Serial.print(';');
                    Serial.write( ":C," );
                    Serial.print( id );
                    Serial.write( ';' );
                }
                break;
                //this block is used for calibrating savox servos
#ifdef ROBOT_SERVICE_CALIBRATE_SERVO
                case ROBOT_SERVICE_CALIBRATE_SERVO: {
                    Serial.write( ":M" );
                    Serial.print( id );
                    Serial.write( ';' );
                    for (int i=0; i<4; i++) {
                        EyeServo[i].write(id);
                    }
                    Serial.write( ":C," );
                    Serial.print( id );
                    Serial.write( ';' );
                }
#endif
                //this block is used for testing the calibration of savox servos
#ifdef ROBOT_SERVICE_TEST_SERVO
                case ROBOT_SERVICE_TEST_SERVO: {
                    Serial.write( ":L" );
                    Serial.print( id );
                    Serial.write( ';' );
                    for (int i=0; i<4; i++) {
                        EyeServoWrite(i, id);
                    }
                    Serial.write( ":C," );
                    Serial.print( id );
                    Serial.write( ';' );
                }
                break;
#endif
#ifdef ROBOT_SERVICE_GO
                case ROBOT_SERVICE_GO: {
                    // Forward declarations.
                    char subCategory;
                    int temp;
                    boolean messageGood = false;
                    numOfVars = sscanf( inBoxBuffer, "%*c%*d,%c,%d", &subCategory, &temp );
                    float firstParam = (float)temp / 120.0; //Convert pixels to feet
                    Serial.write("Feet=");
                    Serial.print(firstParam);
                    // Should have received 2 parameters.
                    if ( numOfVars == 2 ) {
                        // Turn.
                        if ( subCategory == ROBOT_COMMAND_TURN ) {
                            if ( firstParam >= -360 && firstParam <= 360 ) {
                                turn( firstParam*120 ); //Uh I guess we wanted degrees not feet
                                messageGood = true;
                            }
                            // Bad angle.
#ifndef NODEBUG
                            else {
                                Serial.write( ':' );
                                Serial.write( ROBOT_RESPONSE_ERROR );
                                Serial.print( ROBOT_SERIAL_ERROR_WRONG_ARGUMENTS );
                                Serial.write( "Error: Bad angle of\"" );
                                Serial.print( firstParam );
                                Serial.write( "\" was greater than 360 or less than -360." );
                                Serial.write( "Message was\"" );
                                Serial.write( inBoxBuffer );
                                Serial.write( "\";" );
                            }
#endif
                        }
                        // forward fuck
                        else if ( subCategory == ROBOT_COMMAND_FORWARD ) {
                            forward( firstParam );
                            messageGood = true;

                        }
                        // Scoot.
                        else if ( subCategory == ROBOT_COMMAND_SCOOT ) {
                            numOfVars = sscanf( inBoxBuffer, "%*c%*d,%*c,%*d,%d", &temp );
                            float angle = (float)temp;
                            if ( numOfVars == 1 ) {
                                if ( angle >= -360 && angle <= 360 ) {
                                    scoot( firstParam, angle );
                                    messageGood = true;
                                }
                                // Bad angle.
#ifndef NODEBUG
                                else {
                                    Serial.write( ':' );
                                    Serial.write( ROBOT_RESPONSE_ERROR );
                                    Serial.print( ROBOT_SERIAL_ERROR_WRONG_ARGUMENTS );
                                    Serial.write( "Error: Bad angle of\"" );
                                    Serial.print( angle );
                                    Serial.write( "\" was greater than 360 or less than -360." );
                                    Serial.write( "Message was\"" );
                                    Serial.write( inBoxBuffer );
                                    Serial.write( "\";" );
                                }
#endif
                            }
                            // Wrong number of arguments to scoot. Should have got 2 but got only 1.
#ifndef NODEBUG
                            else {
                                Serial.write( ':' );
                                Serial.write( ROBOT_RESPONSE_ERROR );
                                Serial.print( ROBOT_SERIAL_ERROR_WRONG_ARGUMENTS );
                                Serial.write( "Error: Wrong number of arguments to scoot. Expecting 2 but 1. Message was\"" );
                                Serial.write( inBoxBuffer );
                                Serial.write( "\";" );
                            }
#endif
                        }
                        // Bad subcategory command.
#ifndef NODEBUG
                        else {
                            Serial.write( ':' );
                            Serial.write( ROBOT_RESPONSE_ERROR );
                            Serial.print( ROBOT_SERIAL_ERROR_WRONG_ARGUMENTS );
                            Serial.write( "Error: Bad sub category of \"." );
                            Serial.print( subCategory );
                            Serial.write( "\";" );
                            Serial.write( "Message was\"" );
                            Serial.write( inBoxBuffer );
                            Serial.write( "\";" );
                        }
#endif
                    }
                    // Wrong number of arguments.
#ifndef NODEBUG
                    else {
                        Serial.write( ':' );
                        Serial.write( ROBOT_RESPONSE_ERROR );
                        Serial.print( ROBOT_SERIAL_ERROR_WRONG_ARGUMENTS );
                        Serial.write( "Error: Wrong number of arguments to the go service. Expecting 1 but there was none. Message was\"" );
                        Serial.write( inBoxBuffer );
                        Serial.write( "\";" );
                    }
#endif
                    // Command succeeded.
                    if ( messageGood ) {
                        Serial.write( ":C," );
                        Serial.print( id );
                        Serial.write( ';' );
                    }
                }
                break;
#endif
#ifdef ROBOT_WAIT_MODE
                //this block is "wait mode," a simple poll for a button
                case ROBOT_WAIT_MODE: {
                    for (int i=0; i<4; i++) {
                        EyeServo[i].write(45);
                    }
                    while(digitalRead(startButton)==HIGH);
                    Serial.write(":W,");
                    Serial.print(id);
                    Serial.write(";");
                    Serial.write( ":C," );
                    Serial.print( id );
                    Serial.write( ';' );
                }
                break;
#endif
#ifdef ROBOT_SERVICE_SCAN
                case ROBOT_SERVICE_SCAN: {

                    float deltaTheta = ROBOT_SCAN_ANGLE/(ROBOT_SCAN_DATA_POINTS-1);
                    unsigned int IRreading[4][ROBOT_SCAN_DATA_POINTS];
                    unsigned int USreading[4][ROBOT_SCAN_DATA_POINTS];

                    for (int pt = 0; pt <= ROBOT_SCAN_DATA_POINTS; pt += 1) {
                        unsigned long lastTime = millis();  //used to establish a minimum read time
                        for (int eye = 0; eye<4; eye++) {
                            EyeServoWrite(eye,pt);
                            USreading[eye][pt] = PingFire(eye);  //this can be slow if we do it 4 times...might need more delicate code
                            IRreading[eye][pt] = analogRead(IRpin[eye]);
                        }
                        while (millis() <= lastTime+DELAY) {} //wait for minimum read time to elapse, if nec
                    }
                    //now send the message
                    Serial.write( ":J," );
                    Serial.print( id );
                    Serial.write( ",");
                    for (int pt = 0; pt <= ROBOT_SCAN_DATA_POINTS; pt += 1) {
                        for (int eye = 0; eye < 4; eye+=1) {
                            Serial.print( char('|'));
                            Serial.print( (eye)); //EyeNum
                            Serial.write( ',' );
                            Serial.print( (pt)); //DataPointNum
                            Serial.write( ',' );
                            Serial.print( (IRreading[eye][pt] & 255)); //IRlsb
                            Serial.write( ',' );
                            Serial.print( (IRreading[eye][pt] >> 8));  //IRmsb
                            Serial.write( ',' );
                            Serial.print( (USreading[eye][pt] & 255)); //USlsb
                            Serial.write( ',' );
                            Serial.print( (USreading[eye][pt] >> 8));  //USlsb
                        }
                    }
                    Serial.write( ';' );
                    for (int rundown = 180; rundown >= 0; rundown-=5){
                        for (int i = 0; i<4; i++) {
                            EyeServoWrite(i,rundown);
                            //                      EyeServo[i].write(0);
                            delay(10);
                        }

                    }
                    Serial.write( ":C," );
                    Serial.print( id );
                    Serial.write( ';' );
                }
                break;
#endif
#ifdef ROBOT_SERVICE_ARM_SERVO
                case ROBOT_SERVICE_ARM_SERVO: {
                    numOfVars = sscanf( inBoxBuffer, "%*c%*d,%d,%d,%d",
                                        &( newArmTheta[0] ), &( newArmTheta[1] ), &( newArmTheta[2] ) );
                    if ( numOfVars == 3 ) {
                        Serial.print( newArmTheta[0] );
                        Serial.write( ',' );
                        Serial.print( newArmTheta[1] );
                        Serial.write( ',' );
                        Serial.print( newArmTheta[2] );
                        Serial.write( ',' );

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
                    Serial.write( ":C," );
                    Serial.print( id );
                    Serial.write( ';' );
                }
                break;
#endif
#ifndef NODEBUG
                default: {
                    Serial.write( ':' );
                    Serial.write( ROBOT_RESPONSE_ERROR );
                    Serial.print( ROBOT_SERIAL_ERROR_NO_SERVICE );
                    Serial.write( "Error: No such service. Message was\"" );
                    Serial.write( inBoxBuffer );
                    Serial.write( "\";" );

                }
#endif
                }
            }
#ifndef NODEBUG
            else {
                Serial.write( ':' );
                Serial.write( ROBOT_RESPONSE_ERROR );
                Serial.print( ROBOT_SERIAL_ERROR_BAD_MESSAGE );
                Serial.write( "Error: Bad message. Message was\"" );
                Serial.write( inBoxBuffer );
                Serial.write( "\";" );
            }
#endif
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
