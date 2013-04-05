// Enable testing
#define TESTING
// For print.
#include <stdio.h>
// Testing macros.
#include "tests.h"
// For strlen()
#include <string.h>


// BEGIN Mock Declarations
#include <malloc.h>
#define boolean bool
#define abs( X ) ( (X) < 0 ? -(X) : (X) )
#define PI 3.14
#define A1 0
#define A2 1
#define A3 1
void delay( int ) {
}
void analogWrite( int, int ) {
}
int digitalRead( int ) {
}
class HardwareSerial {
  public:
    const char* buffer;
    int nextChar;
    char outBuffer[1000];
    int out_nextChar;
    HardwareSerial( )
            : nextChar( 0 ), out_nextChar( 0 ) {
        outBuffer[0] = '\0';
    }
    char read() {
        char ret = buffer[ nextChar ];
        if ( ret ) {
            ++nextChar;
        }
        return ret;
    }
    int available() {
        return strlen( buffer + nextChar );
    }
    void write( char out ) {
        outBuffer[ out_nextChar++ ] = out;
        outBuffer[ out_nextChar ] = '\0';
    }
    void write( const char* out ) {
        int len = strlen( out );
        strcpy( outBuffer + out_nextChar, out );
        out_nextChar += len;
    }
    void flush() {
    }
    void begin( int ) {
    }
    void print( int out ) {
        int len = sprintf( outBuffer + out_nextChar, "%d", out );
        out_nextChar += len;
    }
};
#include <Servo.h>
void Servo::write( int ) {
}
uint8_t Servo::attach( int ) {
}
Servo::Servo( ) {
}
HardwareSerial Serial;
#define A0 0
#define A1 0
#define OUTPUT 0x1
#define INPUT 0x0
#define LOW  0x0
#define HIGH 0x1
typedef unsigned char uint8_t;
void digitalWrite(uint8_t pin, uint8_t val) {
}
void pinMode(uint8_t, uint8_t) {
}
void delayMicroseconds(unsigned int us) {
}
unsigned long pulseIn(uint8_t pin, uint8_t state, unsigned long timeout = 1000000L) {
}
unsigned long millis(void) {
    static int time = 0;
    return time++;
}
int analogRead(uint8_t pin) {
}
// END Mock Declarations

// Pull in test file.
#include "../ld.ino"



// Forward declaration.
int goodBehavior_TestSuite();

/**
 * Main calls test_suite() and returns results.
 *
 * @return the number of failures.
 */
int main() {
  printf( "line %d\n", __LINE__ );
	int ret=goodBehavior_TestSuite();
	return ret;
}

// BEGIN Results
/// Holds the number of failed assertions.
int bad_asserts = 0;
/// Holds the number of total assertions.
int total_assertions = 0;
/// Holds the number of failed tests.
int bad_tests = 0;
/// Holds the number of total tests.
int total_tests = 0;
// END Results


/**
 * Proves decodeMessage will convert a string message into
 *  a decodedMessage in most cases.
 *
 * @return TRUE if the test succeeds.
 */
bool goodBehavior_loop() {
  bool status = true;
  ++total_tests;
  char type;
  int id;
  TEST_EQUAL( 2,  sscanf( "L123", "%c%d", &type, &id ) );
  TEST_EQUAL( 'L',  type );
  TEST_EQUAL( 123,  id );
  printf( "line %d\n", __LINE__ );
  // Check an empty message.
  {
      Serial.buffer = ":J123;";
      Serial.nextChar = 0;
      Serial.out_nextChar = 0;
      Serial.outBuffer[0] = '\0';
      const char* expected = ":C,123;";
  printf( "line %d\n", __LINE__ );
      loop();
  printf( "line %d\n", __LINE__ );
      char * temp = Serial.outBuffer;
      char * lastColon = (char*)-1;
      while ( *temp != '\0' ) {
        if ( *temp == ':' )
            lastColon = temp;
        ++temp;
      }
      TEST_( lastColon != (char*)-1,
            printf( "FAILURE BECAUSE: expected \"%s\" and actual was \"%s\".\n", expected, Serial.outBuffer ) );
      TEST_( strcmp( expected, lastColon ) == 0,
            printf( "FAILURE BECAUSE: expected \"%s\" and actual was \"%s\".\n", expected, lastColon ) );
      if ( !status ) {
        printf( "outbuffer: %s\n", Serial.outBuffer );
        printf( "type: %c\n", type );
        printf( "id: %d\n", id );
        printf( "lastColon: %s\n", lastColon );
      }
  }
  printf( "line %d\n", __LINE__ );

  // Check a bad service.
  {
      Serial.buffer = ":*123;";
      Serial.nextChar = 0;
      Serial.out_nextChar = 0;
      Serial.outBuffer[0] = '\0';
      loop();
      char type;
      int id;
      TEST_EQUAL( 6, Serial.nextChar );
      TEST_EQUAL( 2, sscanf( Serial.outBuffer, ":%c%d%*s;", &type, &id ) );
      TEST_EQUAL( ROBOT_RESPONSE_ERROR, type );
      TEST_EQUAL( ROBOT_SERIAL_ERROR_NO_SERVICE, id );
      if ( !status ) {
        printf( "outbuffer: %s\n", Serial.outBuffer );
        printf( "type: %c\n", type );
        printf( "id: %d\n", id );
        printf( "Serial.out_nextChar: %d\n", Serial.out_nextChar );
        printf( "Serial.nextChar: %d\n", Serial.nextChar );
      }
  }
  printf( "line %d\n", __LINE__ );

  // Check a bad message.
  {
      Serial.buffer = ":123;";
      Serial.nextChar = 0;
      Serial.out_nextChar = 0;
      Serial.outBuffer[0] = '\0';
      loop();
      char type;
      int id;
      TEST_EQUAL( 2, sscanf( Serial.outBuffer, ":%c%d%*s;", &type, &id ) );
      TEST_EQUAL( ROBOT_RESPONSE_ERROR, type );
      TEST_EQUAL( ROBOT_SERIAL_ERROR_BAD_MESSAGE, id );
      if ( !status ) {
        printf( "outbuffer: %s\n", Serial.outBuffer );
        printf( "type: %c\n", type );
        printf( "id: %d\n", id );
      }

      Serial.buffer = ":ta123;";
      Serial.nextChar = 0;
      loop();
      TEST_EQUAL( 2, sscanf( Serial.outBuffer, ":%c%d%*s;", &type, &id ) );
      TEST_EQUAL( ROBOT_RESPONSE_ERROR, type );
      TEST_EQUAL( ROBOT_SERIAL_ERROR_BAD_MESSAGE, id );
      if ( !status ) {
        printf( "outbuffer: %s\n", Serial.outBuffer );
        printf( "type: %c\n", type );
        printf( "id: %d\n", id );
      }
  }
  printf( "line %d\n", __LINE__ );

  // Check a incomplete message.
  {
      Serial.buffer = ":123";
      Serial.nextChar = 0;
      Serial.out_nextChar = 0;
      Serial.outBuffer[0] = '\0';
      loop();
      char type;
      int id;
      TEST_EQUAL( 2, sscanf( Serial.outBuffer, ":%c%d%*s;", &type, &id ) );
      TEST_EQUAL( ROBOT_RESPONSE_ERROR, type );
      TEST_EQUAL( ROBOT_SERIAL_ERROR_BAD_MESSAGE, id );
      if ( !status ) {
        printf( "outbuffer: %s\n", Serial.outBuffer );
        printf( "type: %c\n", type );
        printf( "id: %d\n", id );
      }

      Serial.buffer = "ta123;";
      Serial.nextChar = 0;
      Serial.outBuffer[0] = '\0';
      loop();
      TEST_EQUAL( 0, strlen( Serial.outBuffer ) );
      if ( !status ) {
        printf( "outbuffer: %s\n", Serial.outBuffer );
        printf( "type: %c\n", type );
        printf( "id: %d\n", id );
      }
  }
  printf( "line %d\n", __LINE__ );

  if ( status )
    printf( "Test %s successful!\n", __FUNCTION__ );
  return status;
}

/**
 * Proves decodeMessage will convert a string message into
 *  a decodedMessage in most cases.
 *
 * @return TRUE if the test succeeds.
 */
bool goodBehavior_readMessage() {
  bool status = true;
  ++total_tests;
  printf( "line %d\n", __LINE__ );
  // Check an empty message.
  {
      Serial.buffer = ":;";
      Serial.nextChar = 0;
      Serial.out_nextChar = 0;
      Serial.outBuffer[0] = '\0';
      TEST_EQUAL( false, readMessage() );
  }
  printf( "line %d\n", __LINE__ );

  if ( status )
    printf( "Test %s successful!\n", __FUNCTION__ );
  return status;
}

bool goodBehavior_confirmations() {
  bool status = true;
  ++total_tests;
  printf( "line %d\n", __LINE__ );
  // Check IR Scan confirmation.
  {
      char buffer[100];
      const char services[] = {
            ROBOT_PING_TEST,
            //ROBOT_SERVICE_CAMERA,
            //ROBOT_SERVICE_IMO,
            ROBOT_PING_TEST,
            ROBOT_SERVICE_SCAN,
            ROBOT_SERVICE_CALIBRATE_SERVO,
            ROBOT_SERVICE_TEST_SERVO,
            //ROBOT_SERVICE_ARM_SERVO,
            ROBOT_SERVICE_GO,
            ROBOT_CALIB_IR,
            ROBOT_WAIT_MODE
      };
  printf( "line %d\n", __LINE__ );
      int serviceCount = sizeof( services );
      for ( int i = 0; i < serviceCount; ++i ) {
  printf( "line %d\n", __LINE__ );
          sprintf( buffer, ":%c%d;", services[ i ], 1014 );
            printf( "input88: \"%s\"\n", buffer );
          Serial.buffer = buffer; //":J1014;";
          Serial.nextChar = 0;
          Serial.out_nextChar = 0;
  printf( "line %d\n", __LINE__ );
          const char* expected = ":C,1014;";
          loop();
  printf( "line %d\n", __LINE__ );
          char * temp = Serial.outBuffer;
          char * lastColon = (char*)-1;
          while ( *temp != '\0' ) {
            if ( *temp == ':' )
                lastColon = temp;
            ++temp;
          }
          TEST_( lastColon != (char*)-1,
                printf( "FAILURE BECAUSE: expected \"%s\" and actual was \"%s\".\n", expected, Serial.outBuffer ) );
          TEST_( strcmp( expected, lastColon ) == 0,
                printf( "FAILURE BECAUSE: expected \"%s\" and actual was \"%s\".\n", expected, lastColon ) );
          if ( !status ) {
            printf( "input: \"%s\"\n", buffer );
            printf( "output: \"%s\"\n", Serial.outBuffer );
            printf( "expected: \"%s\"\n", expected );
          }
      }
  }

  if ( status )
    printf( "Test %s successful!\n", __FUNCTION__ );
  return status;
}

/**
 * Runs "good" behavor tests.
 *
 * @return the number of failures
 */
int goodBehavior_TestSuite(){
  bad_asserts = 0;
  total_assertions = 0;
  printf( "line %d\n", __LINE__ );
  printf( "BEGIN Good Behavior Tests\n");
  printf( "line %d\n", __LINE__ );
  if ( !goodBehavior_confirmations() )
    ++bad_tests;
  if ( !goodBehavior_loop() )
    ++bad_tests;
  printf( "line %d\n", __LINE__ );

    // Run each test and count the successes.
  printf( "line %d\n", __LINE__ );


  printf( "END Good Behavior Tests\n");

    // Prints results.
  printf( "%d of %d assertions successful!\n", (total_assertions - bad_asserts), total_assertions );
  printf( "%d of %d tests successful!\n", (total_tests - bad_tests), total_tests );

    // Print status.
  if( bad_tests == 0 )
    printf("Success!\n");
  else
    printf("Failure!\n");

  return bad_tests;
}


