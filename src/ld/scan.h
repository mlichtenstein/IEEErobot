#if defined( ROBOT_SERVICE_SCAN ) && !defined( GUARD_SCAN_HEADER )
#define GUARD_SCAN_HEADER
#define DELAY 55
extern Servo EyeServo[4];
extern int IRpin[];
void setupScan();
int PingFire(int servoNum);
void EyeServoWrite(int servoNum, int pt);
#endif
