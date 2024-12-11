#include <Arduino.h>
#include <iostream>
#include <HTTPClient.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <inttypes.h>
#include <stdio.h>

#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "Wire.h"
#include "DHT20.h"
#include <string>
#include <Servo.h>
#include "pitches.h"

#define DIGITAL_PIN 33
#define ANALOG_PIN 32
#define MAX_AVGS 40
#define THRESHOLD_MAX 10

Servo servo;
DHT20 DHT;
uint8_t count = 5;
uint32_t micVal;
uint16_t originalSampleSize = 100;
uint16_t sampleSize = 100;
uint8_t fusCnt = 0;
uint8_t agitCnt = 0;
uint8_t distCnt = 0;
uint8_t numAvgs = 0;
double FUSSY;
double AGITATED;
double DISTRESSED;
int SPINSECONDS = 5000;

boolean increasing = true;

char ssid[50]; // your network SSID (name)
char pass[50]; // your network password (use for WPA, or use as key for WEP)

const char kHostname[] = "http://3.14.146.168:5000/data";
const int kNetworkTimeout = 30 * 1000;
const int kNetworkDelay = 1000;
int startTime;

int melody[] = {
  NOTE_C4, NOTE_G3, NOTE_A3, NOTE_G3, NOTE_E3, 
  NOTE_D4, NOTE_C4, NOTE_G3, NOTE_E3, NOTE_C3, 
  NOTE_D4, NOTE_E4, NOTE_C4, NOTE_G3, NOTE_C4
};


void nvs_access() {
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES ||
    err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    err = nvs_flash_init();
  }
  ESP_ERROR_CHECK(err);
  Serial.printf("\n");
  Serial.printf("Opening Non-Volatile Storage (NVS) handle... ");
  nvs_handle_t my_handle;
  err = nvs_open("storage", NVS_READWRITE, &my_handle);
  if (err != ESP_OK) {
    Serial.printf("Error (%s) opening NVS handle!\n", esp_err_to_name(err));
  } 
  else {
    Serial.printf("Done\n");
    Serial.printf("Retrieving SSID/PASSWD\n");
    size_t ssid_len;
    size_t pass_len;
    err = nvs_get_str(my_handle, "ssid", ssid, &ssid_len);
    err |= nvs_get_str(my_handle, "pass", pass, &pass_len);

    switch (err) {
      case ESP_OK:

        Serial.printf("Done\n");
        Serial.printf("SSID = %s\n", ssid);
        Serial.printf("PASSWD = %s\n", pass);
        break;

      case ESP_ERR_NVS_NOT_FOUND:
        Serial.printf("The value is not initialized yet!\n");
        break;

      default:
        Serial.printf("Error (%s) reading!\n", esp_err_to_name(err));
    }
  }
  nvs_close(my_handle);
}


void rotateMobile() {
  //spin mobile for 5 seconds
  int initial = millis();
  while(millis() < initial+SPINSECONDS)
  {
    servo.write(count);
    delay(80);
    if(increasing) {
      count+=2;
      if(count >= 150) {
        increasing = false;
      }
    }
    else {
      if(count <= 3)
      {
        increasing = true;
      }
      count-=2;
    } 
  }
}

void playMusic() {
  // plays the lullaby once
  int length = sizeof(melody) / sizeof(melody[0]);

  for(int k = 0; k < 1; k++) {
    for(int i = 0; i < length; i++)
    {
      tone(25, melody[i], 500);
      delay(500);
      noTone(25);
    }
  }
}

void sendData(double currentMicVal, const char* state) {
  int err = 0;

  HTTPClient http;
  http.begin(kHostname);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");

  int status = DHT.read();
  char kPath[120] = "humidity=";
  char kPath2[] = "&temp=";
  char kPath3[] = "&mic=";
  char kPath4[] = "&state=";
  char kPath5[] = "&time=";
  char humidityVal[10];
  char tempVal[10];
  char micVal[10];
  char timeStamp[10];

  strcat(kPath, dtostrf(DHT.getHumidity(), 4, 3, humidityVal));
  strcat(kPath, kPath2);
  strcat(kPath, dtostrf(DHT.getTemperature(), 4, 3, tempVal));
  strcat(kPath, kPath3);
  strcat(kPath, dtostrf(currentMicVal, 4, 3, micVal));
  strcat(kPath, kPath4);
  strcat(kPath, state);
  strcat(kPath, kPath5);
  strcat(kPath, dtostrf(millis(), 4, 3, timeStamp));

  // Serial.println(kPath);
  err = http.POST(kPath);
  // Serial.println(err);

  if (err > 0 && status == DHT20_OK) {
    String response = http.getString();
    if(response.length() > 0) {
      Serial.println("Response received: " + response);
    } else {
      Serial.println("Getting response failed");
    }
    delay(1000);
  } else {
    Serial.print("Connect failed: ");
    Serial.println(err);
  }
  http.end();
}

void setup() {
  pinMode(DIGITAL_PIN, INPUT);
  pinMode(ANALOG_PIN, INPUT);
  Serial.begin(9600);
  delay(1000);

  servo.attach(15);
  servo.write(5);
  Wire.begin();
  nvs_access();

  WiFi.mode(WIFI_STA);
  delay(1000);
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  DHT.begin();
  WiFi.begin(ssid, pass);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    Serial.print(WiFi.status());
  }

  Serial.println("");
  Serial.println("WiFi connected");

  double cnt = 0;
  for(int i = 0; i < 500; i++) {
    delay(10);
    cnt += analogRead(ANALOG_PIN);
  }
  double avgQuiet = cnt/500;
  Serial.println("Calibrated Quiet:");
  Serial.println(avgQuiet);
  FUSSY = avgQuiet+50;
  AGITATED = FUSSY+50;
  DISTRESSED = AGITATED+50;

  // Serial.println("FUSSY: ");
  // Serial.println(FUSSY);
  // Serial.println("AGITATED: ");
  // Serial.println(AGITATED);
  // delay(2000);

  startTime = millis();
}

void loop() { 
  int err = 0;

  if(sampleSize == 0) {
    numAvgs++;
    sampleSize = originalSampleSize;
    double currentAvg = micVal/(double)sampleSize;
    if(currentAvg > DISTRESSED) {
      distCnt++;
    }
    else if(currentAvg > AGITATED) {
      agitCnt++;
    }
    else if(currentAvg > FUSSY) {
      fusCnt++;
    }

    if(numAvgs == MAX_AVGS) {
      // Analyzed 40 averages and if 10/40
      // are past a threshold, increase that count

      if(fusCnt > THRESHOLD_MAX) {
        sendData(currentAvg, "F");
        playMusic();
        Serial.println("play music");
        delay(2000);
      } 
      else if(agitCnt > THRESHOLD_MAX) {
        sendData(currentAvg, "A");
        rotateMobile();
        Serial.println("spin baby mobile");
        delay(2000);
      }
      else if(distCnt > THRESHOLD_MAX/2) {
        sendData(currentAvg, "D");
        Serial.println("send email notif");
        delay(2000);
      }
      else {
        Serial.println("quiet baby");
        sendData(currentAvg, "Q");
      }

      fusCnt = 0;
      agitCnt = 0;
      distCnt = 0;
      numAvgs = 0;
    }
    micVal = 0;
  }
  else {
    micVal += analogRead(ANALOG_PIN);
    sampleSize--;
  }

}
