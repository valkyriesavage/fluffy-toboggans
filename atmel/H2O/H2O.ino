/**
 * H20IQ Arudino Code
 *
 */
#include <Servo.h>
const int MOISTURE_SENSOR = A0; // PC0=A0 Signal Voltage
const int MOISTURE_VCC = 6; // PD6=D6 VCC for MoistureSensor
const int MOISTURE_GND = 8; // PB0=D8 GND for Moisture Sensor
const int MOISTURE_NONE = 54; // Analog Voltage when no water
const int MOISTURE_FULL = 200; // Analog Voltage when full water
//const int TEMP_SENSOR = A1; // PC1=A1 Signal Voltage
//const int TEMP_VCC = 4; // PD4=D4 VCC for Temp Sensor
//const int TEMP_GND = 2; // PD2=D2 GND for Temp Sensor
//const int TEMP_0 = 54; // Analog signal when temp is 0 deg C
//const int TEMP_100 = 200; // Analog signal when temp is 100 deg C

const int CHIP_RESET = A2; // PC2=A2 Pin that resets the chip when held high.
const int XBEE_SLEEP = 3; // PD3 the pin that tells the XBEE to either wake or sleep

const int SERVO_SIGNAL = 5; // PD5 = D5
//TODO: Alter crystal pin to emit power as DIO
// http://arduino.cc/forum/index.php/topic,37369.0.html
//const int SERVO_POWER =  21//PB7=D21 to turn on Servo power
const int SERVO_OFF_POS = 0;
const int SERVO_ON_POS = 160;
int current_servo_pos = 0;    // variable to store the servo position
Servo actuator;

int num_seconds_to_transmit = 1;
char current_mode = 'N';
int current_high=100; // percent moisture
int current_low=0; // percent moisture

int current_moisture = -1;
int current_temp = -1;

// Button Press Constants
//const int LED = 9;	// PB1= D9LED for button press ack.
const int BLINK_LENGTH = 20; // In milliseconds?
// Need to add buttons here
const int BUTTON_UR = 10;	// PB2= D10 Button
const int BUTTON_LR = 11;	// PB3= D11 Button
const int BUTTON_UL = 12;	// PB4= D12 Button
const int BUTTON_LL = 13;	// PB5= D13 Button

// Battery Monitoring
const int  pSDA = A4; //PC4=A4  for two-wire signal
const int  pSCL =  A5; //PC5=A5  for two-wire clock
const int  BATT_VOLTAGE =  A3; //PC3 = A3  Battery Voltage Pin

void setup() {
  Serial.begin(9600);
  // May need to add XBee comm. setup here
  // Some kind of handshake maybe?
  // Init Button pullup resistors?

  pinMode(MOISTURE_SENSOR, INPUT);
  pinMode(MOISTURE_VCC, OUTPUT);
  pinMode(MOISTURE_GND, OUTPUT);
  digitalWrite(MOISTURE_VCC,HIGH);
  digitalWrite(MOISTURE_GND,LOW);

  //pinMode(TEMP_SENSOR, INPUT);
  //pinMode(TEMP_VCC, OUTPUT);
  //pinMode(TEMP_GND, OUTPUT);
  //digitalWrite(TEMP_VCC,HIGH);
  //digitalWrite(TEMP_GND,LOW);

  //pinmode(SDA, OUTPUT);
  //pinmode(SCL, OUTPUT);
  //pinmode(BATT_VOLTAGE, INPUT);

  //pinmode(SERVO_POWER,OUTPUT);
  // Sets the crystal pins high, check what happens to other pins
  //DDRB = (1<<DDB7)
  // DDRB = (1<<DDB7)|DDRB // Maybe ok?
  pinMode(SERVO_SIGNAL,OUTPUT);
  pinMode(CHIP_RESET,OUTPUT);
  digitalWrite(CHIP_RESET,LOW);
  pinMode(XBEE_SLEEP,OUTPUT); 
}

void set_valve(int pos){
  // Actuate the servo
  //digitalWrite(SERVO_POWER,HIGH); // Turns of Darlington Transistor
  // Sets the servo powerl pin high
  //PORTB = (1<<PORTB7);	// Probably erases other current pins...
  actuator.attach(SERVO_SIGNAL);  // Digital pin
  actuator.write(pos);              // Open valve
  actuator.detach();  // Digital pin
  //digitalWrite(SERVO_POWER,LOW); // Turns off Darlington Transistor
  //PORTB = (0<<PORTB7);
  current_servo_pos = pos;
}

void start_water(){
  set_valve(SERVO_ON_POS);
}

void stop_water(){
  set_valve(SERVO_OFF_POS);
}

void power_xbee(boolean on) {
  if (on) { // Wakes up when XBEE_SLEEP pin is low
    digitalWrite(XBEE_SLEEP, LOW);
  } else {	// XBee goes to sleep when the XBEE_SLEEP pin is high
    digitalWrite(XBEE_SLEEP, HIGH);
  }
}

boolean xbee_io(){
  // Clear the Serial buffer, in case there was any stuff left in there from previous
  Serial.flush();

  // Wake the XBee up
  power_xbee(true);
  // Will take some time for the XBee to wake up and establish a connection, so delay
  delay(200);

  // Send something to Pi
  // Write out current moisture (and temp?) reading to Pi
  Serial.print('M');
  Serial.println(current_moisture);
  //Serial.print('T');
  //Serial.println(current_temp);

  // delay in order to give the Pi time to compute and respond
  delay(200);	

  // Read Pi commands into serial buffer
  int start_time = millis();
  while ( !Serial.available()  && millis()-start_time < 2000) {	// Only wait 2 seconds milliseconds
    delay(2);
  }
  if(Serial.available() >= 1){
    int new_mode = Serial.read();
    if('1' == new_mode ){ // No new command
    // do nothing
    }else{	// Waiting for a new command
      start_time = millis();

      while (Serial.available() < 2) {	// Only wait 2 seconds milliseconds
        if(millis()-start_time < 2000){	// Connection timed out
          // Power off the XBee, and retry
          power_xbee(false);
          Serial.flush();
	  return false;
        }
	delay(2);
      }

      // Danger here if we have some weird remnants still in the buffer.
      // Serial.flush() above should take care of this though.
      int new_high = Serial.read();
      int new_low = Serial.read();

      // Set appropriate flags for main loop
      if(char(new_mode) == 'M'){	// Change to Manual Mode
        current_mode = 'M';
	if(new_high >= 0 && new_high <=100){ // Valid Range
          current_high = new_high;
        }
      }else if(char(new_mode) == 'A'){ // Change to Auto Mode
        if(new_high >= 0 && new_high <=100){ // Valid Range
          current_high = new_high;
        }
        if(new_low >= 0 && new_low <=100){ // Valid Range
          current_low = new_low;
        }
      }
    }
  }
  Serial.flush();	// Flush the buffer, just in case
  // If everything went well, power off the XBee
  power_xbee(false);
  return true;
}

void check_actuation(){
  // Check the current mode
  if('M' == current_mode) {
    if(current_moisture <current_high && current_servo_pos == SERVO_OFF_POS){ 
      // We need to water!
      start_water();
    } else if( current_moisture >=current_high){
      stop_water();
      current_mode = 'N';
    }
  } else if('A' == current_mode){ // Automatic mode
    if(current_moisture < current_low && current_servo_pos == SERVO_OFF_POS) {
      start_water();	
    } else if (current_moisture >= current_high) {
      stop_water();
    }
  }
}

int convert_moisture(int new_moisture){
  return map(new_moisture, MOISTURE_NONE, MOISTURE_FULL, 0, 100); 
}

/*
int convert_temp(int new_temp){
	return map(new_temp, TEMP_0, TEMP_100, 0, 100); 
}
*/

void loop() {
  start_water();
  delay(500);
  stop_water();
  /*
  // Sleep Mode thingy?
  // Most of the time the remaining stuff will be skipped
  
  // Update the moisture and temperature readings
  int current_moisture = convert_moisture(analogRead(MOISTURE_SENSOR));
  //int current_temp = convert_temp(analogRead(TEMP_SENSOR));

  // Check for Xbee communication
  if(millis()%(num_seconds_to_transmit*1000)){
    boolean success = false;
    int num_tries = 0;
    do{
      success = xbee_io();
      if(!success){
        num_tries = num_tries +1;
	delay(1000);
      }
    }while(!success && num_tries < 5);
    // If still hasn’t succeeded, we should try again next cycle (or just wait)
  }
  // Senses water level and actuates Servo
  if(current_mode != 'N'){
    check_actuation();
  }
  */
}
