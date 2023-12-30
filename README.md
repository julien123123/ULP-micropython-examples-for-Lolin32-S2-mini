# ULP-micropython-examples-for-Lolin32-S2-mini
Examples of  micropython codes that are tested to work on the Lolin32 S2 mini with the library esp32_ulp

# Dependencies
ESP32_ULP: https://github.com/micropython/micropython-esp32-ulp 
# Micopython versions
tested on 1.22.0
should work on 1.20 and over at least
# Compatibility / adaptation
Technicaly, since the assembly code is written for the S2, it should work on all ESP32s2 and ESP32s3 boards. The Lolin 32 s2 mini has a led on Pin 15, and we can play with the boot button on pin 0 for testing. For finding the right registers, look at the example scripts in the ESP32_ULP library (at ESP32_ULP: https://github.com/micropython/micropython-esp32-ulp)
