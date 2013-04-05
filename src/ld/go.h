#if defined( ROBOT_SERVICE_GO ) && !defined( GUARD_GO_HEADER )
#define GUARD_GO_HEADER
void scoot(double distance, double angle);

void go(double x, double y, double theta);
void turn(double angle);


void right(double Angle);

void left(double Angle);

void forward(double feet);

void reverse(double feet);
void motorSpeed(double inSpeed);

void wheelAngle(double FL_SERVO, double FR_SERVO);

void faceWheels(double angle);

void ackSolve(float theta, double motorSpeed);

void ackTest();
void setupGo() ;
#endif
