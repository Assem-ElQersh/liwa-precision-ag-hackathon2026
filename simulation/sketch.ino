/*
  In-Situ Ground Sensor Probe Node Simulation (ESP32)
  Arab Youth Space Hackathon 2026 | Team: Liwa Green
  Theme: Precision Agriculture & Crop Intelligence (Liwa Oasis)

  Hardware Components Simulated:
  - ESP32-WROOM-32 Microcontroller
  - Multi-parameter Subsurface Soil Probe (Moisture % & Salinity EC)
  - 0.96" I2C SSD1306 OLED Display (128x64)
  - Automated Solenoid Irrigation Valve (Relay Module on GPIO 23)
  - Status LED (GPIO 19)
*/

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Pin Assignments
const int PIN_MOISTURE = 34;   // Analog Input from Soil Moisture Probe
const int PIN_SALINITY = 35;   // Analog Input from Soil EC / Salinity Probe
const int PIN_VALVE_RELAY = 23;// Digital Output to Solenoid Valve Relay
const int PIN_STATUS_LED = 19; // Digital Output to Status LED

// Agricultural Thresholds for Date Palm (Phoenix dactylifera)
const float MOISTURE_THRESHOLD_LOW = 25.0; // % Volumetric Water Content (Triggers Irrigation)
const float SALINITY_LEACHING_THRESHOLD = 4.0; // dS/m Electrical Conductivity (Triggers Leaching)

void setup() {
  Serial.begin(115200);
  
  pinMode(PIN_VALVE_RELAY, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_VALVE_RELAY, LOW);
  digitalWrite(PIN_STATUS_LED, LOW);

  // Initialize OLED Display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED initialization failed");
  } else {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(10, 20);
    display.println("LIWA PROBE NODE");
    display.setCursor(10, 35);
    display.println("Initializing...");
    display.display();
    delay(1500);
  }
}

void loop() {
  // Read Simulated Sensor Voltages (12-bit ADC: 0 to 4095)
  int raw_moist = analogRead(PIN_MOISTURE);
  int raw_salinity = analogRead(PIN_SALINITY);

  // Convert to physical units
  // Moisture: 0 to 100% Volumetric Water Content
  float moisture_pct = (raw_moist / 4095.0) * 100.0;
  
  // Salinity EC: 0 to 12.0 dS/m (Decisiemens per meter)
  float ec_salinity = (raw_salinity / 4095.0) * 12.0;
  
  // Simulated Soil Temperature (degrees Celsius)
  float soil_temp = 28.5 + (sin(millis() / 10000.0) * 3.5);

  // Control Logic: Open valve if moisture is low OR if salinity requires leaching
  bool valve_active = false;
  String irrigation_reason = "STANDBY";

  if (moisture_pct < MOISTURE_THRESHOLD_LOW) {
    valve_active = true;
    irrigation_reason = "DEFICIT";
  } else if (ec_salinity > SALINITY_LEACHING_THRESHOLD) {
    valve_active = true;
    irrigation_reason = "LEACHING";
  }

  // Actuate Hardware
  if (valve_active) {
    digitalWrite(PIN_VALVE_RELAY, HIGH);
    digitalWrite(PIN_STATUS_LED, HIGH);
  } else {
    digitalWrite(PIN_VALVE_RELAY, LOW);
    digitalWrite(PIN_STATUS_LED, LOW);
  }

  // Update OLED Display
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("LIWA OASIS NODE 01");
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);

  display.setCursor(0, 16);
  display.print("Moist: ");
  display.print(moisture_pct, 1);
  display.print(" %");

  display.setCursor(0, 28);
  display.print("Salin: ");
  display.print(ec_salinity, 2);
  display.print(" dS/m");

  display.setCursor(0, 40);
  display.print("Temp : ");
  display.print(soil_temp, 1);
  display.print(" C");

  display.setCursor(0, 53);
  display.print("Valve: ");
  if (valve_active) {
    display.print("ON (");
    display.print(irrigation_reason);
    display.print(")");
  } else {
    display.print("OFF [OPTIMAL]");
  }
  display.display();

  // Transmit Telemetry over Serial (JSON for Gateway/Cloud Integration)
  Serial.print("{\"node\":\"LIWA_PROBE_01\",");
  Serial.print("\"moist_pct\":");
  Serial.print(moisture_pct, 1);
  Serial.print(",\"ec_dsm\":");
  Serial.print(ec_salinity, 2);
  Serial.print(",\"temp_c\":");
  Serial.print(soil_temp, 1);
  Serial.print(",\"valve_active\":");
  Serial.print(valve_active ? "true" : "false");
  Serial.print(",\"mode\":\"");
  Serial.print(irrigation_reason);
  Serial.println("\"}");

  delay(1000);
}
