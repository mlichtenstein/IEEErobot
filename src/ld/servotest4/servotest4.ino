#include <Servo.h>

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
Servo R1,R2_1,R2_2,R3;
int newTheta[] = {0,0,0};
int oldTheta[] = {0,0,0};
int thetaCount = 0;
void setup() 
{
  R1.attach(3);
  R2_1.attach(5);
  R2_2.attach(6);
  R3.attach(10);
  Serial.begin(9600);
  inputString.reserve(200);
  pinMode(8, OUTPUT); // end effector pin
}

void loop() 
{
  
  if (stringComplete) 
  {
    Serial.println(inputString);
    
    String tempString = "";
    thetaCount = 0;
    Serial.println(inputString.length());
    
    for(int j= 0; j <= inputString.length(); j++)
    {
      if(inputString[j] == 'i')
      {
        digitalWrite(8, HIGH);
      }
      if(inputString[j] == 'o')
      {
        digitalWrite(8, LOW);

      }
      if(isDigit(inputString[j]))
        tempString += (char)inputString[j];
      if(inputString[j] == ',')
      {
        newTheta[thetaCount] = tempString.toInt();
        tempString = "";
        thetaCount += 1;
      }


    }
    
    
    newTheta[2] = 280 - newTheta[2];
    Serial.print("oldTheta: ");
    for(int i = 0; i < 3; i++)
    {
      Serial.print(oldTheta[i]);
      Serial.print(',');
    }
    Serial.println();
    Serial.print("newTheta: ");
    for(int j = 0; j < 3; j++)
    {
      Serial.print(newTheta[j]);
      Serial.print(',');
    }   
    Serial.println();
 
    //write out angles
    for(int i = 1; i <= 2000; i++)
    {
        R1.writeMicroseconds((int)(convertR1(oldTheta[0]) + (convertR1(newTheta[0]) - convertR1(oldTheta[0]))*i/2000));
        R2_1.writeMicroseconds((int)(convertR2_1(oldTheta[1]) + (convertR2_1(newTheta[1]) - convertR2_1(oldTheta[1]))*i/2000));
        R2_2.writeMicroseconds((int)(convertR2_2(oldTheta[1]) + (convertR2_2(newTheta[1]) - convertR2_2(oldTheta[1]))*i/2000));
        R3.writeMicroseconds((int)(convertR3(oldTheta[2]) + (convertR3(newTheta[2]) - convertR3(oldTheta[2]))*i/2000));
      delay(1);
    }
    
    //clean up
    for(int i = 0; i < 3; i++)
    {
      oldTheta[i] = newTheta[i];
    }
    delay(15);
    Serial.println("done");
    stringComplete = false;
    inputString = "";
  }
}

void serialEvent() // pull in a string
{
  while (Serial.available()) 
  {
    char inChar = (char)Serial.read(); 
    inputString += inChar;
    if (inChar == 'f')
    { 
      stringComplete = true;
    }
  }
}

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
