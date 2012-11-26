/**
 * Some simple code for reading a sensor and printing it over serial.
 *
 * released into the wild by Mark, Shiry, & Valkyrie in 2012
 */
#include <Servo.h> 
const int HUMIDITY_SENSOR = A0;
const int SERVO_SIGNAL = 9;
const int LED = 13;
const int OFF_POS = 0;
const int ON_POS = 160;

const int ON_LENGTH = 20;

Servo watertube;

int pos = 0;    // variable to store the servo position
boolean water_plant =false;

void setup() {
  Serial.begin(9600);
  pinMode(HUMIDITY_SENSOR, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
    int incoming = Serial.read();
    water_plant= true;
  }
  
  Serial.println(analogRead(HUMIDITY_SENSOR));
  
  if(water_plant){
    // Actuate the servo
    watertube.attach(SERVO_SIGNAL);  // Digital pin
    for(pos = 0; pos < ON_POS; pos += 1)  // goes from 0 degrees to 180 degrees
    {                                  // in steps of 1 degree
      watertube.write(pos);              // tell servo to go to position in variable 'pos'
      delay(10);                       // waits 15ms for the servo to reach the position
    }
    delay(1000);
    for(pos = ON_POS; pos>=1; pos-=1)     // goes from 180 degrees to 0 degrees
    {                                
      watertube.write(pos);              // tell servo to go to position in variable 'pos'
      delay(10);                       // waits 15ms for the servo to reach the position
    }
    watertube.write(0);
    watertube.detach();  // Digital pin
    water_plant =false;
  }
  delay(1000);
}
