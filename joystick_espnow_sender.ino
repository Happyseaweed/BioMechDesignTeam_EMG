/*
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/esp-now-esp32-arduino-ide/
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
  
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*/

#include <esp_now.h>
#include <WiFi.h>

// REPLACE WITH YOUR RECEIVER MAC Address
uint8_t broadcastAddress[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

// PIN can be defined, but needs to be 36, 37, 38, 39, and 32, 33, 34, 35 
// IF we are using ESP-NOW along with it.
#define READ_X_PIN 34
#define READ_Y_PIN 35
int x = 0;
int y = 0;

// Structure example to send data
// Must match the receiver structure
typedef struct struct_message {
  char a[32];
    int x_val;
    int y_val;
} struct_message;

// Create a struct_message called myData
struct_message myData;

esp_now_peer_info_t peerInfo;

// callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}
 
void setup() {
  // Serial baud rate, 9600 is default, 115200 is another rate used.
  Serial.begin(9600);
 
  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  // Once ESPNow is successfully Init, we will register for Send CB to
  // get the status of Trasnmitted packet
  esp_now_register_send_cb(OnDataSent);
  
  // Register peer
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  
  // Add peer        
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Failed to add peer");
    return;
  }
}
 
void loop() {
  // Reading values (joystick) from pins
  // CONSIDER: uint8_t, uint16_t, etc. Fixed width integer range.
  x = analogRead(READ_X_PIN);
  y = analogRead(READ_Y_PIN);

  // Set values to send
  // NOTE: This depends on the data structure defined above, this MUST match
  // the data structure the receiver has.
  Serial.print(x);
  Serial.print(", ");
  Serial.print(y);
  Serial.print("\n");
  strcpy(myData.a, "Joystick Data");
  myData.x_val = x;
  myData.y_val = y;
  
  // Send message via ESP-NOW
  esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &myData, sizeof(myData));
   
  if (result == ESP_OK) {
    Serial.println("Sent with success");
  }
  else {
    Serial.println("Error sending the data");
  }
  delay(200);
}
