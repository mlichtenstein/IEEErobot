#ifndef TESTS_HEADER_INCLUDED
#define TESTS_HEADER_INCLUDED

extern int bad_asserts;
extern int total_assertions;
extern int bad_tests;
extern int total_tests;

#define TEST_( A, FAIL_OUTPUT ) \
  {\
    ++total_assertions;\
    if ( !(A) ){\
      FAIL_OUTPUT;\
      printf( "Actual: %s = %s\nExpected: True\n", #A, "FALSE" );\
      printf( "Assertion failed!\nMore Info: File \"%s\"\nLine: %i Function: \"%s\"\n",__FILE__,__LINE__,__FUNCTION__ );\
      ++bad_asserts;\
      status = false;\
    }\
  }
#define TEST_FLOAT( A, B, TOLERANCE ) \
  {\
    double actual = A;\
    double expected = B;\
    ++total_assertions;\
    if (ABS( actual - expected ) > TOLERANCE ){\
      printf( "Actual: %s = %f\nExpected: %s = %f\n", #A, actual, #B, expected );\
      printf( "Assertion failed!\nMore Info: File \"%s\"\nLine: %i Function: \"%s\"\n",__FILE__,__LINE__,__FUNCTION__ );\
      ++bad_asserts;\
      status = false;\
    }\
  }
#define TEST_EQUAL( E, A ) \
  {\
    ++total_assertions;\
    if ( E != A ){\
      printf( "Expected: %s = %d\nActual: %s = %d\n", #E, E, #A, A );\
      printf( "Assertion of \"%s == %s\" failed!\nMore Info: File \"%s\"\nLine: %i Function: \"%s\"\n",#E,#A,__FILE__,__LINE__,__FUNCTION__ );\
      ++bad_asserts;\
      status = false;\
    }\
  }
#endif // TESTS_HEADER_INCLUDED

