# import hcsr04
#
# hr = hcsr04.HCSR04("Y5","Y6")
#
# while 1:
#     print(hr.distance_mm())


import sys
import pyb
import machine
import random

button_exept = 0
try:

#    import my_main_mouse
    #import my_main_send_to_lora
    #import my_main_drone2
    import my_main_roboracer
#	import MHZ19B


except Exception as e:
    count=1
    sw = pyb.Switch()

    button_exept = 0
    def press():
        global button_exept
        button_exept = 1

    sw.callback(press)
    while True:
        sys.print_exception(e)
        print('~~~~~~~~~~~~~')
	break
        pyb.delay(100)
        # count+=1
        if button_exept==0:
#              machine.reset()
              pass



