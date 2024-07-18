
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "DESKTOP-KCUII6Q 3899";                 // WiFi SSID
const char* password = "Vk4453-4";                         //WiFi password
//2
const char* serverUrl = "http://192.168.1.120:8080/data";  //  Flask server URL

int ldrPin = 34;  // Pin where the LDR is connected
int green = 27;
int red = 14;
int yellow = 13;
String floodlightStatus = "OFF";

void setup() {
  Serial.begin(115200);
  pinMode(ldrPin, INPUT);
  pinMode(red, OUTPUT);     // led pin
  pinMode(green, OUTPUT);   // led pin
  pinMode(yellow, OUTPUT);  // led pin

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  int ldrValue = analogRead(ldrPin);
  Serial.println(ldrValue);

  Serial.print("Lux: ");
  Serial.println(ldrValue);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String httpRequestData = "{\"ldr_value\": " + String(ldrValue) + "}";
    int httpResponseCode = http.POST(httpRequestData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
  
// Set the threshold
if (ldrValue < 700) {
  digitalWrite(green, HIGH);
  digitalWrite(red, HIGH);
  digitalWrite(yellow, HIGH);  // Switch on all the Floodlight
  floodlightStatus = "ON";
} else {
  digitalWrite(green, LOW);
  digitalWrite(red, LOW);  // Turn off the floodlights
  digitalWrite(yellow, LOW);
  floodlightStatus = "OFF";
}

Serial.print("Floodlightstatus: ");
Serial.println(floodlightStatus);


  delay(5000);  // send a request every 5 seconds
}
