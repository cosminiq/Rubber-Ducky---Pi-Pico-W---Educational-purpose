import os
import board
import digitalio
import rotaryio
import asyncio
import time
from boot import pico_w_usb_drive_state # constant form the boot file

#============== Libray for Lcd =========================================
import busio
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
#============== Libray for LDC =========================================

#=================== Parsing the Payload code===========================n
from ducky import *
#=======================================================================

# ============ Create an instance of the encoder =======================
encoder = rotaryio.IncrementalEncoder(board.GP5, board.GP6)
button_pin = digitalio.DigitalInOut(board.GP12)
button_pin.direction = digitalio.Direction.INPUT
button_pin.pull = digitalio.Pull.UP
# ======================================================================

#============ LCD ======================================================
i2c = busio.I2C(board.GP17, board.GP16)
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=2, num_cols=16)
# Talk to the LCD at I2C address 0x27.
# The number of rows and columns defaults to 4x20, so those
# arguments could be omitted in this case.
#=======================================================================

# ============ Define the directory to read files from ================
dir_path = "/Payload"
#=======================================================================

#================== Welcome msg on LCD =================================
def welcome_msg():
    lcd.clear()
    lcd.set_cursor_pos(0, 0)
    lcd.print(" PI Pico Ducky")
    lcd.set_cursor_pos(1, 0)
    lcd.print("  Hacking tool" )
welcome_msg()
#=======================================================================

#======== Print message on LCD afther payload start ==================== 
def print_file(filename):
    lcd.clear()
    lcd.set_cursor_pos(0, 0)
    lcd.print("SELECT   PAYLOAD")
    lcd.set_cursor_pos(1, 0)
    lcd.print(filename)
#======================================================================================================================

# ===== Define a function to get the list of files in the directory ====================================================
def get_file_list():
    return sorted(os.listdir(dir_path))
#=========================================================================================================================

#== Define a function to get the name of the file at a given index in the list
def get_file_name(index):
    file_list = get_file_list()
    return file_list[index]
#=============================================================================================================================

#======== Blink Function =====================================================================================================
async def blink(pin, interval, count):
    while True:
        with digitalio.DigitalInOut(pin) as led:
            led.switch_to_output(value=False)
            for _ in range(count):
                led.value = True
                await asyncio.sleep(interval)  # Don't forget the "await"!
                led.value = False
                await asyncio.sleep(interval)  # Don't forget the "await"!
#============================================================================================================================
# ========= Define an asynchronous function to monitor the encoder and print the name of the next or previous file =========
async def monitor_encoder_and_button():
    current_file_index = 0
    file_list = get_file_list()
    while True:
        position = encoder.position
        if position != 0:
            current_file_index += position
            if current_file_index < 0:
                current_file_index = len(file_list) - 1
            elif current_file_index >= len(file_list):
                  current_file_index = 0
            print(current_file_index+1, get_file_name(current_file_index).replace(".txt", ""))
            
            text_lcd =(str(current_file_index+1)+". "+str(get_file_name(current_file_index).replace(".txt", ""))) # variabila care converteste textul in string din alte variabile
            print_file(text_lcd) # cheama functie cu variabila str ca vor aparea ca text in LCD display
            encoder.position = 0
            
        if not button_pin.value:
            filename = dir_path + "/" + get_file_name(current_file_index)
            runScript(filename) # variabila din fisierul cod ducky
            #exec(open(filename).read(), globals()) # deschide orice fisier din memorie in urma selectiei
            
        await asyncio.sleep(0.01)
# ============================================================================================================================
#========================= Function that acting like loop ====================================================================
async def main():
    if pico_w_usb_drive_state == True: # verificare si afisare pe led in stadiu este raspberry pi pico adica mass storage or not
        led1_task = asyncio.create_task(blink(board.GP13, 0.1, 10))
    else:
        led2_task = asyncio.create_task(blink(board.GP11, 0.25, 20))
    
    monitor_task = asyncio.create_task(monitor_encoder_and_button())
    await asyncio.gather(monitor_task)  # Don't forget "await"!
# ============================================================================================================================    

asyncio.run(main())



