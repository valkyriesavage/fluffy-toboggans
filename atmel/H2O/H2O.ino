/**
 * H20IQ Arudino Code
 *
 */
#include <Servo.h>
const int MOISTURE_SENSOR = A0; // PC0=A0 Signal Voltage
const int MOISTURE_VCC = 6; // PD6=D6 VCC for MoistureSensor
const int MOISTURE_GND = 8; // PB0=D8 GND for Moisture Sensor
const int MOISTURE_NONE = 550; // Analog Voltage when no water
const int MOISTURE_FULL = 650; // Analog Voltage when full water
double dmois = 50;
//const int TEMP_SENSOR = A1; // PC1=A1 Signal Voltage
//const int TEMP_VCC = 4; // PD4=D4 VCC for Temp Sensor
//const int TEMP_GND = 2; // PD2=D2 GND for Temp Sensor
//const int TEMP_0 = 54; // Analog signal when temp is 0 deg C
//const int TEMP_100 = 200; // Analog signal when temp is 100 deg C

const int CHIP_RESET = A2; // PC2=A2 Pin that resets the chip when held high.
const int XBEE_SLEEP = 3; // PD3 the pin that tells the XBEE to either wake or sleep
boolean com_success = false;

const int SERVO_SIGNAL = 5; // PD5 = D5
//TODO: Alter crystal pin to emit power as DIO
// http://arduino.cc/forum/index.php/topic,37369.0.html
const int SERVO_POWER =  2; //PB7=D21 to turn on Servo power
const int SERVO_OFF_POS = 180;
const int SERVO_ON_POS = 90;
int current_servo_pos = SERVO_OFF_POS;    // variable to store the servo position
Servo actuator;

int num_seconds_to_transmit = 1;
char current_mode = 'A';
int current_high=90; // percent moisture
int current_low=30; // percent moisture

int current_moisture = 50;
int current_temp = -1;

// Button Press Constants
const int LED = 9;	// PB1= D9LED for button press ack.
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
unsigned long last_communication = 0;
unsigned long last_reading = 0;

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

  pinMode(SERVO_POWER,OUTPUT);
  // Sets the crystal pins high, check what happens to other pins
  //DDRB = (1<<DDB7)
  // DDRB = (1<<DDB7)|DDRB // Maybe ok?
  pinMode(SERVO_SIGNAL,OUTPUT);
  pinMode(CHIP_RESET,OUTPUT); 
  digitalWrite(CHIP_RESET,LOW);
  pinMode(XBEE_SLEEP,OUTPUT);
  power_xbee(true);
  
  // Buttons
  pinMode(LED,OUTPUT);
  pinMode(BUTTON_UR,INPUT_PULLUP);
  pinMode(BUTTON_UL,INPUT_PULLUP);
  pinMode(BUTTON_LR,INPUT_PULLUP);
  pinMode(BUTTON_LL,INPUT_PULLUP);
  
  // Initialization Blink
  blink_led(500,7);
}

void set_valve(int pos){
  //Serial.println(pos);
  // Actuate the servo
  //digitalWrite(SERVO_POWER,HIGH); // Turns on Darlington Transistor
  //delay(100);  // Give it some time to power up
  actuator.attach(SERVO_SIGNAL);  // Digital pin
  for(int i =0 ; i<5;i++){  // Do a few times to make siure
    delay(100);
    actuator.write(pos);              // Open valve
  }
  delay(10);  
  actuator.detach();  // Digital pin
  //delay(10);
  //digitalWrite(SERVO_POWER,LOW); // Turns off Darlington Transistor
  current_servo_pos = pos;
}

void start_water(){
  set_valve(SERVO_ON_POS);
}

void stop_water(){
  set_valve(SERVO_OFF_POS);
}

// Works
void power_xbee(boolean on) {
  if (on) { // Wakes up when XBEE_SLEEP pin is low
    digitalWrite(XBEE_SLEEP, LOW);
  } else {	// XBee goes to sleep when the XBEE_SLEEP pin is high
    digitalWrite(XBEE_SLEEP, HIGH);
  }
}

void blink_led(int time,int num_times){
  for(int i =0;i<num_times; i++){
    digitalWrite(LED,HIGH);
    delay(time);
    digitalWrite(LED,LOW);
    delay(time);
  }
}

void serial_flush_buffer()
{
  while (Serial.read() >= 0)
   ; // do nothing
}

boolean xbee_io(){

  // Clear the Serial buffer, in case there was any stuff left in there from previous
  serial_flush_buffer();

  // Wake the XBee up
  power_xbee(true);
  // Will take some time for the XBee to wake up and establish a connection, so delay
  delay(200);

  // Send something to Pi
  // Write out current moisture (and temp?) reading to Pi
  // Serial.print('M');
  Serial.println(current_moisture);
  Serial.flush();
  //Serial.print('T');
  //Serial.println(current_temp);
  // delay in order to give the Pi time to compute and respond
  delay(1000);	

  // Read Pi commands into serial buffer
  long start_time = millis();
  int num_passes = 0;
  //Serial.print("m:"); Serial.print(millis());Serial.print("s:");Serial.print(start_time);
//  while ( !Serial.available()  && millis()-start_time < 2000) {	// Only wait 2 seconds
  while ( !Serial.available()  && num_passes < 10) {	// Only wait 2 seconds
    delay(100);
    num_passes = num_passes +1;
    //Serial.print('.');
  }
  if(Serial.available() >= 1){
    char new_mode = Serial.read();
    //Serial.print("r:");
    //Serial.println(int(new_mode));
    if('1' == new_mode ){ // No new command
    // do nothing
      // Blink LED if we have received transmission
      blink_led(100,2);
      
    }else if('r' == new_mode){
      reset_chip();
    }else{	// Waiting for a new command
      start_time = millis();
      
      while (Serial.available() < 2) {	// Only wait 2 seconds
        if(millis()-start_time > 2000){	// Connection timed out
          // Power off the XBee, and retry
          //power_xbee(false);
          //serial_flush_buffer();
          //Serial.print("m:"); Serial.print(millis());Serial.print("s:");Serial.print(start_time);
          return false;
        }
      	delay(2);
        //Serial.println(Serial.available());
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
        Serial.print("Setting Manual mode to high: ");
        Serial.println(current_high);
      }else if(char(new_mode) == 'A'){ // Change to Auto Mode
        current_mode = 'A';
        if(new_high >= 0 && new_high <=100){ // Valid Range
          current_high = new_high;
        }
        if(new_low >= 0 && new_low <=100){ // Valid Range
          current_low = new_low;
        }
        Serial.print("Setting Automatic mode to high: ");
        Serial.print(current_high);
        Serial.print(" and low: ");
        Serial.println(current_low);
      }
      blink_led(1000,1);
    }
    //Serial.print("Serial Remaining: ");
    //Serial.println(Serial.available());
    serial_flush_buffer();
    return true;
  }
  //Serial.print("A:");
  //Serial.println(Serial.available());

  //Serial.print("A:");
  //Serial.println(Serial.available());
  // If everything went well, power off the XBee
  //power_xbee(false);
    
  //serial_flush_buffer();	// Flush the buffer, just in case
  return false;
}

void check_actuation(){
  // Check the current mode
  if('M' == current_mode) {
    if(current_moisture <= current_high && current_servo_pos == SERVO_OFF_POS){ 
      // We need to water!
      //Serial.println("Turning on Servo");
      start_water();
    } else if( current_moisture >= current_high && current_servo_pos == SERVO_ON_POS){
      stop_water();
      //Serial.println("Turning off Servo");
      current_mode = 'N';
    }
  } else if('A' == current_mode){ // Automatic mode
    //print_current_mode();
    //Serial.println(current_servo_pos);
    if(current_moisture <= current_low && current_servo_pos == SERVO_OFF_POS) {
      start_water();	
      //Serial.println("Turning on Servo");
    } else if (current_moisture >= current_high && current_servo_pos == SERVO_ON_POS ) {
      stop_water();
      //Serial.println("Turning off Servo");
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

void button_debug(){
  Serial.print(digitalRead(BUTTON_UR));
  Serial.print(',');
  Serial.print(digitalRead(BUTTON_UL));
  Serial.print(',');
  Serial.print(digitalRead(BUTTON_LR));
  Serial.print(',');
  Serial.print(digitalRead(BUTTON_LL));
  Serial.println();  
}

void servo_debug(){
  if(digitalRead(BUTTON_UR)==LOW){
    start_water();
  }else if(digitalRead(BUTTON_UL)==LOW){
    stop_water();
  }
  delay(100);
}

void led_debug(){
//  boolean any_pressed = !(digitalRead(BUTTON_UR) && digitalRead(BUTTON_UL) );
  boolean any_pressed = !(digitalRead(BUTTON_UR) && digitalRead(BUTTON_LR) && digitalRead(BUTTON_UL) && digitalRead(BUTTON_LL));
  if(any_pressed){
    digitalWrite(LED,HIGH);
  }
  else{
    digitalWrite(LED,LOW);
  }
}

void dtr_debug(){
  if(digitalRead(BUTTON_UL)==LOW){
    power_xbee(false);
  }
  else{
    power_xbee(true);
  }
}

void reset_debug(){
  if(digitalRead(BUTTON_LL)==LOW){
    reset_chip();
  }  
}

int step_moisture(boolean watering){
  // Simulates water moisture for servo testing
  unsigned long current_reading = millis();
  double err = random(100)/100;
  double time_speed = 2.5;
  //double err = 0;
  double lambda = 0;
  if(watering){
    lambda = 0.02*time_speed;
  }else{
    // Exponential Decay
    lambda = -0.01*time_speed;
  }
  //Serial.println((current_reading-last_reading)/double(1000));
  dmois = dmois + lambda*dmois*(current_reading-last_reading)/double(1000);
  // Cap it at 100;
  dmois = constrain(dmois,5,100);
  last_reading=current_reading;
  //Serial.println(dmois + err);
  return int(dmois + err);
  
}

void print_current_mode(){
  Serial.print("Mode: ");
  Serial.print(current_mode);
  Serial.print(" Mois: ");
  Serial.print(current_moisture);
  if('N'!= current_mode){
    Serial.print(" H: ");
    Serial.print(current_high);
  }
  if('A'== current_mode){
    Serial.print(" L: ");
    Serial.print(current_low);
  }
  Serial.println();
}

void reset_control(){
  if(digitalRead(BUTTON_LR)==LOW && digitalRead(BUTTON_UR)==LOW){
    reset_chip();
  }
}

// From:
// http://www.faludi.com/itp_coursework/meshnetworking/XBee/XBee_program_Arduino_wireless.html
void reset_chip() {
   /* if the project does not typically receive data, and accidental chip resets are tolerable,
   * this is a simple method that should work just fine. Otherwise it is recommended that the 
   * reset request string be part of a call-response sequence, be transmitted with a
   * reserved byte or byte string, or be transmitted in some way out of band, so that it is not 
   * accidentally received.
   */
   Serial.print("\nArduino will reset in ");
   Serial.print(5);
   Serial.print(" seconds...\n\r");
   blink_led(500,5);
   Serial.print("\nResetting NOW.\n\r");
   digitalWrite(CHIP_RESET, HIGH); // switch on a transistor that pulls the chip's reset pin to ground
}

void loop() {
  
  delay(100);
  //button_debug();
  led_debug();
  //dtr_debug();
  //servo_debug();
  //reset_debug();
  reset_control();
  
  // Sleep Mode thingy?
  // Most of the time the remaining stuff will be skipped
  
  // Update the moisture and temperature readings
  //current_moisture = convert_moisture(analogRead(MOISTURE_SENSOR));
  //current_moisture = analogRead(MOISTURE_SENSOR);
  //current_moisture = random(100);
  current_moisture = step_moisture(current_servo_pos == SERVO_ON_POS);
  //int current_temp = convert_temp(analogRead(TEMP_SENSOR));
  //Serial.println(analogRead(MOISTURE_SENSOR));
  //Serial.println(current_moisture);
  //Serial.println(random(10));
  
  
  // Check for Xbee communication
  
  //if(millis()%(num_seconds_to_transmit*1000)){
  if((millis()-last_communication) > num_seconds_to_transmit*1000 ){
    int num_tries = 0;
    do{
      com_success = xbee_io();
      //Serial.print("Success: ");
      //Serial.println(success);
      if(!com_success){
        //Serial.println("No communication");
        num_tries = num_tries +1;
	//delay(500);
      }
    }while(!com_success && num_tries < 5);
    // If still hasn’t succeeded, try again next time
    last_communication = millis();
  }
  
  // Senses water level and actuates Servo
  if(current_mode != 'N'){
    check_actuation();
  }
  
}
