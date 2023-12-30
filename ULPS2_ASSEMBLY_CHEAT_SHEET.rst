=====================
ULP S2 ASSEMBLY CHEAT SHEET 
=====================

This is by no mean a reference, this is just my own cheat cheat with the codes I use the most
please refer to https://docs.espressif.com/projects/esp-idf/en/latest/esp32s2/api-reference/system/ulp_instruction_set.html for a comprehensive list of the instructions


``LD`` Destination, Data to load

``ST`` Data to store, destination, offset (usually  0)

``MOVE`` register, (variable, constant or number)

``AND`` (bitwise and) result register, register to compare 1, register to compare 2. if 1&2 =1 -> result =1, anything else(if we keep registers btweewn 1 and 0) = 0

``OR`` (bitwise or)result register, register to compare 1, register to compare 2. (if we keep registers btweewn 1 and 0) if register 1 and register 2 = 0, r1 or r2 = 0, everything else =1

``SUB`` result register, register 1, register 2 (result = r1-r2)

``ADD`` result register, register 1, register 2 (result = r1+r2)

``JUMP`` name of code section, (EQ Condition = JUMP result of last operation is 0)

``JUMPR`` name of code section (jump with base as r0), treshold
    conditions:
        ◦ EQ (equal) – jump if value in R0 == threshold
        ◦ LT (less than) – jump if value in R0 < threshold
        ◦ LE (less or equal) – jump if value in R0 <= threshold
        ◦ GT (greater than) – jump if value in R0 > threshold
        ◦ GE (greater or equal) – jump if value in R0 >= threshold
        
``HALT``  End the Program
``WAKE`` Wake up the Chip
``WAIT`` cycles - Wait Some Number of Cycles


MACROS:
-----------------------------
READ_RTC_REG(rtc_reg, low_bit, bit_width)
          
READ_RTC_FIELD(rtc_reg, field)
          
WRITE_RTC_REG(rtc_reg, low_bit, bit_width, value)
          
WRITE_RTC_FIELD(rtc_reg, field, value)
