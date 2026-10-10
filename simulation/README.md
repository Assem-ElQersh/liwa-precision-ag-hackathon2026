# Liwa Oasis IoT Ground Sensor Node -- Interactive Wokwi Simulation

This directory contains the complete browser-based hardware and firmware simulation for the **In-Situ Ground Sensor Probe Node** (Arab Youth Space Hackathon 2026).

---

## What This Simulates
- **ESP32 Microcontroller:** Core controller running automated precision irrigation logic.
- **Subsurface Soil Moisture Sensor:** Analog potentiometer mapping 0% to 100% Volumetric Water Content (VWC).
- **Subsurface Salinity Sensor:** Analog potentiometer mapping 0 to 12.0 dS/m Electrical Conductivity (EC).
- **0.96" I2C OLED Display:** Real-time in-field readout of soil moisture, salinity, temperature, and valve state.
- **Solenoid Irrigation Valve Relay & LED:** Actuates automatic drip irrigation when root-zone moisture drops below 25% or when soil salinity exceeds 4.0 dS/m (leaching requirement).
- **Telemetry Stream:** Serial JSON packets formatted for cloud / satellite integration.

---

## How to Run in 60 Seconds (Zero Electronics Background Required)

1. Open your browser and go to: **[https://wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32)**
2. In the code tab (`sketch.ino`), select all and paste the contents of [`simulation/sketch.ino`](sketch.ino).
3. In the circuit tab (`diagram.json`), select all and paste the contents of [`simulation/diagram.json`](diagram.json).
4. Click the green **Play** button at the top.
5. In the Library Manager tab (`libraries.txt` in Wokwi), add:
   ```
   Adafruit SSD1306
   Adafruit GFX Library
   ```
6. **Interact with the simulation:**
   - Turn the **Soil Moisture** dial down below 25% to trigger deficit irrigation. Notice the OLED screen update to `Valve: ON (DEFICIT)`, the relay click, and the green valve LED turn on.
   - Turn the **Soil Salinity EC** dial up above 4.0 dS/m to trigger leaching irrigation (`Valve: ON (LEACHING)`).
   - Turn both dials to normal values to watch the system return to `Valve: OFF [OPTIMAL]`.
