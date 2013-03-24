#include <Servo.h>
#include <math.h>

//Coordinates of wheel stems in cartesian plane with origin at center of bot
#define BODY_WIDTH 4.515625
#define BODY_LENGTH 3.6875

//Front-left servo, etc
Servo FLSERVO, FRSERVO, BLSERVO, BRSERVO;
//Pin numbers for wheel servos, motor pairs
const int LEFT_DIR1 = 22, LEFT_DIR2 = 23, RIGHT_DIR1 = 24, RIGHT_DIR2 = 25;
const int LEFT_SPEED = 2, RIGHT_SPEED = 3;

void setup() 
{ //Attach Servos
  Serial.begin(9600);
  FLSERVO.attach(50); //front left servo
  FRSERVO.attach(51); //front right servo
  BLSERVO.attach(52); //back left servo
  BRSERVO.attach(53); //back right servo
  pinMode(LEFT_DIR1, OUTPUT);
  pinMode(LEFT_DIR2, OUTPUT);
  pinMode(RIGHT_DIR1, OUTPUT);
  pinMode(RIGHT_DIR2, OUTPUT);
}

void loop() 
{ 
        //go(0,1,0);go(2,0,0);
        forward(3); delay(500);reverse(3);
        while(1){int i = 0;}
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
