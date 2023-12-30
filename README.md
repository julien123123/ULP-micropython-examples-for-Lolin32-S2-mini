# ULP-micropython-examples-for-Lolin32-S2-mini
Examples of  micropython codes that are tested to work on the Lolin32 S2 mini with the library esp32_ulp

I decided to publish those files since there aren't many example programs written for the ULP with the micropython esp32_ULP library. I hope this helps some gain more insights as to how a working, tested ULP assembly program looks like.

# Dependencies
ESP32_ULP: https://github.com/micropython/micropython-esp32-ulp 
# Micopython versions
tested on 1.22.0
should work on 1.20 and over at least
# Compatibility / adaptation
Technicaly, since the assembly code is written for the S2, it should work on all ESP32s2 and ESP32s3 boards. The Lolin 32 s2 mini has a led on Pin 15, and we can play with the boot button on pin 0 for testing. For finding the right registers, look at the example scripts in the ESP32_ULP library (at ESP32_ULP: https://github.com/micropython/micropython-esp32-ulp)
# CHEAT SHEET
I included my sheet I used as I'm not accostumed to write in assembly. Here it is:
https://github.com/julien123123/ULP-micropython-examples-for-Lolin32-S2-mini/blob/a6a0abe4d90df1be5b61f8c65428350823198b0d/ULPS2_ASSEMBLY_CHEAT_SHEET.rst
Be aware that it might contain errors,
