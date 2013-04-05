#if defined( ROBOT_SERVICE_GO ) && !defined( GUARD_GO_HEADER )
#define GUARD_GO_HEADER
void scoot(double distance, int angle);

void go(double x, double y, int theta);
void turn(int angle);


void right(int Angle);

void left(int Angle);

void forward(int feet);

void reverse(int feet);
void motorSpeed(int inSpeed);

void wheelAngle(int FL_SERVO, int FR_SERVO);

void faceWheels(int angle);

void ackSolve(float theta, double motorSpeed);

void ackTest();
void setupGo() ;
#endif
