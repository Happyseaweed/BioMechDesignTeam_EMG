/*
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleServer.cpp
    Ported to Arduino ESP32 by Evandro Copercini
    updates by chegewara
*/

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include "BluetoothSerial.h"
#include <algorithm>

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHAR_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
BluetoothSerial SerialBT;

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pChar = NULL;

void setup() {
  //   Serial.begin(115200);
  //   BTSerial.begin();
  //   Serial.println("Starting BLE work!");

  //   BLEDevice::init("Long name works now");
  //   BLEServer *pServer = BLEDevice::createServer();
  //   BLEService *pService = pServer->createService(SERVICE_UUID);
  //   BLECharacteristic *pCharacteristic = pService->createCharacteristic(
  //                                          CHARACTERISTIC_UUID,
  //                                          BLECharacteristic::PROPERTY_READ |
  //                                          BLECharacteristic::PROPERTY_WRITE
  //                                        );

  //   pCharacteristic->setValue("Hello hello, this is the ESP32 Bluetooth Server!");
  //   pService->start();
  //   // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still is working for backward compatibility
  //   BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  //   pAdvertising->addServiceUUID(SERVICE_UUID);
  //   pAdvertising->setScanResponse(true);
  //   pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  //   pAdvertising->setMinPreferred(0x12);
  //   BLEDevice::startAdvertising();
  //   Serial.println("Characteristic defined! Now you can read it in your phone!");
    
    
    Serial.begin(115200);
    SerialBT.begin();
    Serial.println("[Arm Server Setup Starting...]");
    // Creating the server
    BLEDevice::init("Arm Server");
    
    pServer = BLEDevice::createServer();
    // pServer->setCallbacks(new MyServerCallBack()); // Custom onConnect methods
    
    pService = pServer->createService(SERVICE_UUID);
    
    pChar = pService->createCharacteristic(
        CHAR_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY
    );
    
    pChar->setValue(
        "This is the characeristic of the service provided by [Arm Server]");
    // pChar->setCallBacks(new MyCallBack());
    pService->start();
    
    // Advertising the server.
    BLEAdvertising *pAdvert = pServer->getAdvertising();
    pAdvert->addServiceUUID(SERVICE_UUID);  
    pAdvert->start();
    Serial.println("[Arm Server Setup Complete]"); 
}


void loop() {
    // put your main code here, to run repeatedly:

    uint8_t sensorValue = analogRead(13);
    Serial.println("Read Value: ");
    Serial.println(sensorValue);
    
    String valToSend = String(sensorValue);
    String test = "123123";
    // pChar->setValue((uint8_t*)&sensorValue, 4);
    Serial.println(valToSend);
    pChar->setValue(valToSend.c_str());
    pChar->notify();


    delay(5);
}
