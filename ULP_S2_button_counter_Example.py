#by Julien Croteau, 30-12-2023
# Based on the example script of the esp32_ulp micropython library's examples
# https://github.com/micropython/micropython-esp32-ulp

'''
This script will read the state of Pin0 of the LOLIN 32s2 (the boot button). It will count start a count and it
will stop it when the button is released. When that happens, the ULP will raise flag, and then the main loop
will print the total count, and lower the flag.

This might be used to handle a button outside of the main loop
'''

from esp32 import ULP
from machine import mem32
import machine
import time

from esp32_ulp import src_to_binary

# To find the address of the variable to read in the main program, the first variable's address is 0, and add 4 for the next one
'''The ULP program is designed to measure the duration of button presses and send the data to the main processor. Here's a high-level overview of the program:

    Initialize the ULP program and set up the GPIO pin for the button.
    Wait for the button to be pressed.
    When the button is pressed, start a counter to measure the duration of the button press.
    Wait for the button to be released.
    When the button is released, stop the counter and store the duration of the button press.
    Wait for a short delay to debounce the button.
    Repeat steps 2-6 until the ULP program is reset.

The ULP program uses a counter to measure the duration of button presses. The counter is incremented every cycle (approximately 800ns) and is stored in memory.
When the button is released, the duration of the button press is calculated by subtracting the value of the counter at the start of the button press from the value of the
counter at the end of the button press.
'''
source = """\
#define DR_REG_RTCIO_BASE            0x3f408400
#define RTC_IO_TOUCH_PAD0_REG       (DR_REG_RTCIO_BASE + 0x94)
#define RTC_IO_TOUCH_PAD0_MUX_SEL_M  (BIT(19))
#define RTC_IO_TOUCH_PAD0_FUN_IE_M   (BIT(13))
#define RTC_GPIO_IN_REG              (DR_REG_RTCIO_BASE + 0x24)
#define RTC_GPIO_IN_NEXT_S           10
#define DR_REG_SENS_BASE             0x3f408800
#define SENS_SAR_IO_MUX_CONF_REG     (DR_REG_SENS_BASE + 0x0144)
#define SENS_IOMUX_CLK_GATE_EN       (BIT(31))
#define DR_REG_RTCCNTL_BASE          0x60008000
#define RTC_CNTL_LOW_POWER_ST_REG    (DR_REG_RTCCNTL_BASE + 0x00CC)
#define RTC_CNTL_RDY_FOR_WAKEUP  	 (BIT(19))
#define RTC_CNTL_MAIN_STATE  		 0x0000000F

#define RTC_IO_XTAL_32P_PAD_REG      (DR_REG_RTCIO_BASE + 0xC0)
#define RTC_IO_X32P_MUX_SEL_M  		 (BIT(19))
#define RTC_GPIO_OUT_REG             (DR_REG_RTCIO_BASE + 0x0)
#define RTC_GPIO_ENABLE_REG          (DR_REG_RTCIO_BASE + 0xc)
#define RTC_GPIO_ENABLE_S            10
#define RTC_GPIO_OUT_DATA_S          10

#define RTCIO_GPIO15_CHANNEL        15
.set gpio, RTCIO_GPIO15_CHANNEL

.set channel, 0
.set token, 0xcafe  # magic token

.text

state:		.long 0
count:		.long 0
magic: 		.long 0
last:		.long 0
flag:		.long 0
final:		.long 0

.global entry

entry:
            move r0, magic
            ld r1, r0, 0

            # test if we have initialised already
            sub r1, r1, token
            Jump after_init, eq  # jump if magic == token (note: "eq" means the last instruction (sub) resulted in 0)
init:
            # enable IOMUX clock
            WRITE_RTC_FIELD(SENS_SAR_IO_MUX_CONF_REG, SENS_IOMUX_CLK_GATE_EN, 1)

            # connect GPIO to the RTC subsystem so the ULP can read it
            WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_MUX_SEL_M, 1, 1)

            # switch the GPIO into input mode
            WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_FUN_IE_M, 1, 1)
            
            # store that we're done with initialisation
            move r0, magic
            move r1, token
            st r1, r0, 0
            
            #prevent a false button release detection for the first run
            move r3, last
            move r0, 1
            st r0, r3, 0
            
after_init:
            # read the GPIO's current state into r0
            READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S + channel, 1)

            # set r3 to the memory address of "state"
            move r3, state

            # store what was read into r0 into the "state" variable
            st r0, r3, 0
            
            ld r2, r3, 0 // load state value to r2
            
            add r1, r2, 0 // add 0 to state
            
            jump plus, eq // jump to plus if state=0
            # else continue
            
            # set r3 to the memory address of "last"
            move r3, last
            
            ld r2, r3, 0 // load last value to r2
            
            add r1, r2, 0 // add 0 to value of last
            
            jump unpress, eq // jump to unpress if last value is 0 (and state is 1)
            
            #else(if value is 1 and state is one)
            
routine:
            # set r3 to the memory address of state
            move r3, state 
            # set r2 to the value of last
            move r2, last
            ld r1, r3, 0
            st r1, r2, 0 // store state in the last state value
            
            # halt ULP co-processor (until it gets woken up again)
exit:
            halt
            
plus:		#set r3 ti the memory address of "count"
            move r3, count
            ld r2, r3, 0 // load count value to r2
            add r2, r2, 1 // add 1 to r2
            st r2, r3, 0 // store the value of r2 in count
            jump routine // go to routine
            
unpress:
            #set r3 ti the memory address of 'count'
            move r3, count
            ld r2, r3, 0 // load count value to r2
            move r1, final
            st r2, r1, 0 // store the value of Count in final
            sub r0, r2, r2 //put the value of r2-r2 in r0
            st r0, r3, 0 // store r2-r2(0) as the new value of count
            move r3, flag
            move r0, 1
            st r0, r3, 0 // store 1 in flag
            jump routine
"""
ULP_MEM_BASE = 0x50000000
ULP_DATA_MASK = 0xffff  # ULP data is only in lower 16 bits

load_addr = 0
ULPvar = ('state','count', 'magic', 'last', 'flag', 'final', 'entry_addr')

# assign all the assembly variables and their addresses to a micropython dict
# Entry address always has to be last because it's the firt live after the
# address variables and is is where the program starts
def var_ULP(tup):
    addr_dict = {value: ULP_MEM_BASE + load_addr + i*4 for i, value in enumerate(tup)}
    if 'entry_addr' in tup:
        addr_dict['entry_addr'] = tup.index('entry_addr') * 4
    return addr_dict

addr_dict = var_ULP(ULPvar)
entry_addr = addr_dict['entry_addr']

binary = src_to_binary(source, cpu="esp32s2")  # cpu is esp32 or esp32s2

ulp = ULP()
ulp.set_wakeup_period(0, 50000)  # use timer0, wakeup after 50.000 cycles
ulp.load_binary(load_addr, binary)

mem32[addr_dict['state']] = 0x1 #set initial state as 1
ulp.run(entry_addr)

while True:
    print(' state: ', int(mem32[addr_dict['state']] & ULP_DATA_MASK))
    flag = int(mem32[addr_dict['flag']] & ULP_DATA_MASK)
    if flag:
        print(int(mem32[addr_dict['final']] & ULP_DATA_MASK))
        mem32[addr_dict['flag']] = 0x0 #set the flag back to 0
        print('button released')
    time.sleep_ms(500) # Added so that the output doesn't overwhelm the repl

