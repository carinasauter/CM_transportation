#include <SPI.h>
#include <avr/dtostrf.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"
#include <WiFi101.h>
#include <Adafruit_GPS.h>
#include <math.h>;
#define GPSSerial Serial1
Adafruit_GPS GPS(&GPSSerial);


uint32_t timer = millis();
char ssid[] = "CarinaWiFi"; //XFSETUP-E66
char pass[] = "testtest"; //around1524curve22
int status = WL_IDLE_STATUS;
#define AIO_SERVER      "io.adafruit.com"
#define AIO_SERVERPORT  1883 //no ssl at this point
#define AIO_USERNAME    "caycay"
#define AIO_KEY         "80009f64496041f79d5f440181eeb727"
#define HomePin 9
#define LocationPin 6
#define ButtonPin 13
WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_SERVERPORT, AIO_USERNAME, AIO_KEY);
#define halt(s) { Serial.println(F( s )); while(1);  }
Adafruit_MQTT_Publish gps_data = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/GPS/csv");
Adafruit_MQTT_Subscribe comeHome = Adafruit_MQTT_Subscribe(&mqtt, AIO_USERNAME "/feeds/comeHome");
Adafruit_MQTT_Subscribe locationRequest = Adafruit_MQTT_Subscribe(&mqtt, AIO_USERNAME "/feeds/locationRequest");
Adafruit_MQTT_Publish alerts_feed = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/alerts");
Adafruit_MQTT_Publish comingHome = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/comingHome");

// Size of the geo fence (in meters)
const float maxDistance = 500;
int buttonState = 0;

void setup() {
  
  //Wifi Setup
  WiFi.setPins(10, 11, 12);
  while (!Serial);
  Serial.begin(115200);
  Serial.println(F("Welcome to Connex"));
  Serial.print(F("\nInit the WiFi module..."));
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WINC1500 not present");
    while (true);
  }
  Serial.println("ATWINC OK!");
  
  // GPS setup
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
//  GPS.sendCommand(PGCMD_ANTENNA);
  delay(1000);

  // MQTT and Pin setup
  mqtt.subscribe(&locationRequest);
  mqtt.subscribe(&comeHome);
  pinMode(HomePin, OUTPUT);
  pinMode(LocationPin, OUTPUT);
  pinMode(ButtonPin, INPUT);
}

void loop() {
  uint8_t num = 0;
  // home longitude and latitude to be able to calculate distance from home
  float homeLat = 37.876022;
  float homeLon = -122.258802;
  
  MQTT_connect();
  
  Adafruit_MQTT_Subscribe *subscription;
  
  // read data from the GPS in the 'main loop'
  char c = GPS.read();
  // if millis() or timer wraps around, we'll just reset it
  if (timer > millis()) timer = millis();  
  // approximately every 10 seconds or so, print out the current stats
  if (millis() - timer > 10000) {
    timer = millis(); // reset the timer
    if (GPS.fix) {
      Serial.print("Latitude: ");
      printFloat(GPS.latitude, 5);
      Serial.println("");

      Serial.print("Longitude: ");
      printFloat(GPS.longitude, 5);
      Serial.println("");

      // Calculate distance from home
      float distance = distanceCoordinates(GPS.latitude, GPS.longitude, homeLat, homeLon);

      Serial.print("Distance: ");
      printFloat(distance, 5);
      Serial.println("");

      if (distance > maxDistance) {
        logAlert(1, alerts_feed);
      }
      logLocation(GPS.latitude, GPS.longitude, GPS.altitude, gps_data);  
    }
    Serial.println("no fix found");  
  }
  while ((subscription = mqtt.readSubscription())) {
    if (subscription == &comeHome) {
      Serial.println((char *)comeHome.lastread);
      for (int i = 0; i < 3; i++) {
        digitalWrite(HomePin, HIGH);
        delay(2000);
        digitalWrite(HomePin, LOW);
        delay(1000); 
      }       
      
    }
    if (subscription == &locationRequest) {
      Serial.println("location request received!");
      for (int i = 0; i < 3; i++) {
        digitalWrite(LocationPin, HIGH);
        delay(2000);
        digitalWrite(LocationPin, LOW);
        delay(1000); 
      }       
    }
  }

  // button push
   buttonState = digitalRead(ButtonPin); 
  if (buttonState == HIGH) {
    logButtonPress(1, comingHome);
    buttonState = LOW;
    delay(1000);
  }
}



void MQTT_connect() {
  int8_t ret;
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    uint8_t timeout = 10;
    while (timeout && (WiFi.status() != WL_CONNECTED)) {
      timeout--;
      delay(1000);
    }
  }
  if (mqtt.connected()) {
    return;
  }
  Serial.print("Connecting to MQTT... ");
  while ((ret = mqtt.connect()) != 0) {
       Serial.println(mqtt.connectErrorString(ret));
       Serial.println("Retrying MQTT connection in 5 seconds...");
       mqtt.disconnect();
       delay(5000);
  }
  Serial.println("MQTT Connected!");
}

uint8_t txFailures = 0;  // Count of how many publish failures have occured in a row.

// Serialize the lat, long, altitude to a CSV string that can be published to the specified feed.
void logLocation(float latitude, float longitude, float altitude, Adafruit_MQTT_Publish& publishFeed) {
  // Initialize a string buffer to hold the data that will be published.
  char sendBuffer[120];
  memset(sendBuffer, 0, sizeof(sendBuffer));
  int index = 0;

  // Start with '0,' to set the feed value.  The value isn't really used so 0 is used as a placeholder.
  sendBuffer[index++] = '0';
  sendBuffer[index++] = ',';

  // Now set latitude, longitude, altitude separated by commas.
  dtostrf(latitude, 2, 6, &sendBuffer[index]);
  index += strlen(&sendBuffer[index]);
  sendBuffer[index++] = ',';
  dtostrf(longitude, 3, 6, &sendBuffer[index]);
  index += strlen(&sendBuffer[index]);
  sendBuffer[index++] = ',';
  dtostrf(altitude, 2, 6, &sendBuffer[index]);

  // Finally publish the string to the feed.
  Serial.print(F("Publishing location: "));
  Serial.println(sendBuffer);
  if (!publishFeed.publish(sendBuffer)) {
    Serial.println(F("Publish failed!"));
    txFailures++;
  }
  else {
    Serial.println(F("Publish succeeded!"));
    txFailures = 0;
  }
}
 
// converts lat/long from Adafruit
// degree-minute format to decimal-degrees
double convertDegMinToDecDeg (float degMin) {
  double min = 0.0;
  double decDeg = 0.0;
 
  //get the minutes, fmod() requires double
  min = fmod((double)degMin, 100.0);
 
  //rebuild coordinates in decimal degrees
  degMin = (int) ( degMin / 100 );
  decDeg = degMin + ( min / 60 );
 
  return decDeg;
}

// from web
void printFloat(float value, int places) {
  // this is used to cast digits 
  int digit;
  float tens = 0.1;
  int tenscount = 0;
  int i;
  float tempfloat = value;

    // make sure we round properly. this could use pow from <math.h>, but doesn't seem worth the import
  // if this rounding step isn't here, the value  54.321 prints as 54.3209

  // calculate rounding term d:   0.5/pow(10,places)  
  float d = 0.5;
  if (value < 0)
    d *= -1.0;
  // divide by ten for each decimal place
  for (i = 0; i < places; i++)
    d/= 10.0;    
  // this small addition, combined with truncation will round our values properly 
  tempfloat +=  d;

  // first get value tens to be the large power of ten less than value
  // tenscount isn't necessary but it would be useful if you wanted to know after this how many chars the number will take

  if (value < 0)
    tempfloat *= -1.0;
  while ((tens * 10.0) <= tempfloat) {
    tens *= 10.0;
    tenscount += 1;
  }


  // write out the negative if needed
  if (value < 0)
    Serial.print('-');

  if (tenscount == 0)
    Serial.print(0, DEC);

  for (i=0; i< tenscount; i++) {
    digit = (int) (tempfloat/tens);
    Serial.print(digit, DEC);
    tempfloat = tempfloat - ((float)digit * tens);
    tens /= 10.0;
  }

  // if no places after decimal, stop now and return
  if (places <= 0)
    return;

  // otherwise, write the point and continue on
  Serial.print('.');  

  // now write out each decimal place by shifting digits one by one into the ones place and writing the truncated value
  for (i = 0; i < places; i++) {
    tempfloat *= 10.0; 
    digit = (int) tempfloat;
    Serial.print(digit,DEC);  
    // once written, subtract off that digit
    tempfloat = tempfloat - (float) digit; 
  }
}


// Calculate distance between two points - from web
float distanceCoordinates(float flat1, float flon1, float flat2, float flon2) {

  // Variables
  float dist_calc=0;
  float dist_calc2=0;
  float diflat=0;
  float diflon=0;

  // Calculations
  diflat  = radians(flat2-flat1);
  flat1 = radians(flat1);
  flat2 = radians(flat2);
  diflon = radians((flon2)-(flon1));

  dist_calc = (sin(diflat/2.0)*sin(diflat/2.0));
  dist_calc2 = cos(flat1);
  dist_calc2*=cos(flat2);
  dist_calc2*=sin(diflon/2.0);
  dist_calc2*=sin(diflon/2.0);
  dist_calc +=dist_calc2;

  dist_calc=(2*atan2(sqrt(dist_calc),sqrt(1.0-dist_calc)));
  
  dist_calc*=6371000.0; //Converting to meters

  return dist_calc;
}

// Log alerts
void logAlert(uint32_t alert, Adafruit_MQTT_Publish& publishFeed) {

  // Publish
  Serial.print(F("Publishing alert: "));
  Serial.println(alert);
  if (!publishFeed.publish(alert)) {
    Serial.println(F("Publish failed!"));
    txFailures++;
  }
  else {
    Serial.println(F("Publish succeeded!"));
    txFailures = 0;
  }
}

void logButtonPress(uint32_t number, Adafruit_MQTT_Publish& publishFeed) {

  // Publish
  Serial.print(F("Publishing button press: "));
  if (!publishFeed.publish(number)) {
    Serial.println(F("Publish failed!"));
    txFailures++;
  }
  else {
    Serial.println(F("Publish succeeded!"));
    txFailures = 0;
  }
}
