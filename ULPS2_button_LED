from esp32 import ULP, wake_on_ulp
from machine import mem32
import machine
import time
from esp32_ulp import src_to_binary

'''
This script will open the mini's led when the button on pin 0 is pressed so you can test the behaviour without additional equipement.
You can see that if you CTRL+D in the repl, the led still lights up when you press the button.
When you do a full reset, the behaviour stops (that is unless you renamed this file as 'main.py')

adapted from the examples of the ESP32_ULP library : https://github.com/micropython/micropython-esp32-ulp

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

#Those are for the led on Pin 15:
#define RTC_IO_XTAL_32P_PAD_REG      (DR_REG_RTCIO_BASE + 0xC0)
#define RTC_IO_X32P_MUX_SEL_M  		 (BIT(19))
#define RTC_GPIO_OUT_REG             (DR_REG_RTCIO_BASE + 0x0)
#define RTC_GPIO_ENABLE_REG          (DR_REG_RTCIO_BASE + 0xc)
#define RTC_GPIO_ENABLE_S            10
#define RTC_GPIO_OUT_DATA_S          10

#define RTCIO_GPIO15_CHANNEL		 15

.set channel, 0
.set token, 0xcafe  # magic token
.set gpio, RTCIO_GPIO15_CHANNEL

state:      .long 0
magic:		.long 0

entry:
 # load magic flag
  move r0, magic
  ld r1, r0, 0

  # test if we have initialised already
  sub r1, r1, token
  jump after_init, eq  # jump if magic == token (note: "eq" means the last instruction (sub) resulted in 0)

init:
            # enable IOMUX clock
            WRITE_RTC_FIELD(SENS_SAR_IO_MUX_CONF_REG, SENS_IOMUX_CLK_GATE_EN, 1)

            # connect GPIO to the RTC subsystem so the ULP can read it
            WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_MUX_SEL_M, 1, 1)

            # switch the GPIO into input mode
            WRITE_RTC_REG(RTC_IO_TOUCH_PAD0_REG, RTC_IO_TOUCH_PAD0_FUN_IE_M, 1, 1)
            # connect GPIO to ULP (0: GPIO connected to digital GPIO module, 1: GPIO connected to analog RTC module)
            WRITE_RTC_REG(RTC_IO_XTAL_32P_PAD_REG, RTC_IO_X32P_MUX_SEL_M, 1, 1);

            # GPIO shall be output, not input (this also enables a pull-down by default)
            WRITE_RTC_REG(RTC_GPIO_ENABLE_REG, RTC_GPIO_ENABLE_S + gpio, 1, 1)
            
            # store that we're done with initialisation
            move r0, magic
            move r1, token
            st r1, r0, 0

after_init:
            # read the GPIO's current state into r0
            READ_RTC_REG(RTC_GPIO_IN_REG, RTC_GPIO_IN_NEXT_S + channel, 1)

            # set r3 to the memory address of "state"
            move r3, state

            # store what was read into r0 into the "state" variable
            st r0, r3, 0
            
            ld r0, r3, 0 // load state value to r0
            
            add r0, r0, 0
            jump pressed, eq #jump to pressed if state+0=0
            
            # else turn off led (clear GPIO)
            WRITE_RTC_REG(RTC_GPIO_OUT_REG, RTC_GPIO_OUT_DATA_S + gpio, 1, 0)


exit:
            # halt ULP co-processor (until it gets woken up again)
            halt

pressed:
            # turn on led (set GPIO)
            WRITE_RTC_REG(RTC_GPIO_OUT_REG, RTC_GPIO_OUT_DATA_S + gpio, 1, 1)
            jump exit
"""
load_addr = 0

ULP_MEM_BASE = 0x50000000
ULP_DATA_MASK = 0xffff  # ULP data is only in lower 16 bits

def var_ULP(tup):
    addr_dict = {value: ULP_MEM_BASE + load_addr + i*4 for i, value in enumerate(tup)}
    if 'entry_addr' in tup:
        addr_dict['entry_addr'] = tup.index('entry_addr') * 4
    return addr_dict
            
ULPvar = ('state', 'magic', 'entry_addr') # Entry address always has to be last because it's the firt live after the address variables and is is where the program starts
addr_dict = var_ULP(ULPvar)
entry_addr = addr_dict['entry_addr']

binary = src_to_binary(source, cpu="esp32s2")  # cpu is esp32 or esp32s2

ulp = ULP()
ulp.set_wakeup_period(0, 50000)  # use timer0, wakeup after 50.000 cycles
ulp.load_binary(load_addr, binary)

ulp.run(entry_addr)
            
while True:
    print(' state: ', int(mem32[addr_dict['state']] & ULP_DATA_MASK))
    time.sleep_ms(300) #I added this so the repl doesn't bug your machine because it's too fast
