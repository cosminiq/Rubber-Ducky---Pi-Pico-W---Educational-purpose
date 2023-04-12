from board import *
import digitalio
import storage
import time
import board

pico_w_usb_drive_state = False
noStorageStatus = False
noStoragePin = digitalio.DigitalInOut(GP0)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
noStorageStatus = not noStoragePin.value


def toggle_led(button_pin, led_pin):
    led = digitalio.DigitalInOut(led_pin)
    led.direction = digitalio.Direction.OUTPUT

    button = digitalio.DigitalInOut(button_pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

    last_press_time = 0
    debounce_delay = 200  # milliseconds
    led_on = False

    while True:
        current_time = time.monotonic_ns() // 1000000  # get current time in milliseconds
        if not button.value:  # button is pressed
            if current_time - last_press_time >= debounce_delay:
                if not led_on:
                    led.value = True  # turn LED on
                    led_on = True
                else:
                    led.value = False  # turn LED off
                    led_on = False
                last_press_time = current_time
        else:  # button is not pressed
            last_press_time = 0
        
        return led_on
   
state = toggle_led(board.GP9, board.GP10)
print(state)

if(noStorageStatus == True):
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    pico_w_usb_drive_state = False
    print("Disabling USB drive")
else:
    # normal boot
    pico_w_usb_drive_state = True
    print("USB drive enabled")

if (state == True):
    storage.disable_usb_drive()
    file_path = "/WEB7_APoint.py"
    with open(file_path) as f:
            code = f.read()
        # Execute the Python code in the file
            exec(code)
