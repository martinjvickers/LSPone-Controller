#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 16:37:51 2018

@author: lspone
Edited by Sam Deans 18:00 20/01/2020
Changelog (for lack of git...)
- Moved all imports to top (and globals to 'if __name__=='__main__' section so this can be imported as a module for debugging)
- Changed default valve to port 6
- Added change_port() function (hotkey 't') to change valve port.
- Deleted various hidden indents etc
- Added position condition to dispense()
- Added help message
- Fixed dispensing bug
- Set waiting times for the motor to run
"""
import time
import serial
import sys
from pynput import keyboard
import os
import msvcrt

helpText = '''
lspONE Keyboard Controls:

a/Left Pedal: Pickup liquid
c/Right Pedal: Dispense all liquid
v: Change the default volume picked up each time (times 8nl)
t: Change the valve port being used
   (The screw holes around the top of the device numbered 1-6)
q: Exit the program (does not shut down device,
   but it seems you can turn it off safely if
   the light is not flashing and the motor is
   not running)
h: Print the help message
i: Initialise (reset the device)

Legacy options from Steffan/manufacturers
p: Push out 100nl from reservoir (not sure what this is for)
f: Fill tube 2 from tube 1 (don't use)
l: Initiate clean: (You won't need this in normal air-based use)
'''

def initialize():
    global posisiton
    lsp.write(b'/1ZB6R\r')
    print('initialising device')
    position = 0

def push_out_100():
    lsp.write(b'/1gB1P120B2D120R\r')
    print('Pushing out 100nl')

def change_volume():
    global stepsize
    global pic_volume
    stepsize = int(input("Choose pickup volume per pedal strike: 1 = 8 nl\n"))
    pic_volume = stepsize * 8
    print ("Pickup volume is: ", pic_volume, "nl")
    return stepsize, pic_volume

def change_port():
    global port
    global setport
    port = input("Type the number port your capillary is screwed into (e.g. 6)\n")
    setport = '/1B' + port + 'R\r'
    lsp.write(setport.encode())
    return port, setport

def fill_tube():
    lsp.write(b'/1gB1P2500B2D2500G15R\r')

def clean_tube():
    lsp.write(b'/1gB1P2500B2D2500G5R\r')

def pickup():
    global position
    global stepsize
    global pic
    position = position + stepsize
    p = str(stepsize)
    p1 =  "/1P" + p + "R\r"
    pic = bytes(p1, 'utf-8')
    lsp.write(pic)
    if stepsize == 1:
        time.sleep(0.25)
    else:
        time.sleep(0.5)
    stop = lsp.read(1)
    print (stop)
    return pic, position

def dispense():
    global position
    global dis
    if position > 0:
        d = str(position)
        d1 = "/1D" + d + "R\r"
        dis = d1.encode()
        lsp.write(dis)
        print('Dispensing...')
        time.sleep(0.5)
        position = position - position
    return dis, position

# This code runs if and only if you ran 'python lspone1.py' from the command line
if __name__=='__main__':
    try:
        lsp = serial.Serial('COM4', 9600, timeout=10) # connect pump
    except serial.serialutil.SerialException:
        sys.stderr.write('You have not connected the lspONE device.\nPlease plug it in and switch it on.\n\n')
        raise
    #initialize pump
    print(helpText)
    lsp.write(b"/1ZR\r")
    print('Waiting for the machine to setup')
    time.sleep(13)
    pic = ""
    dis = ""
    position = 0 # Initial plunger position
    # Prompt user to set step size. One step corresponds to 8nl
    stepsize = int(input("Choose initial pickup volume per pedal strike: 1 = 8 nl\n"))
    pic_volume = stepsize * 8
    print ("Pickup volume is: ", pic_volume, "nl\ndispension is always total volume")
    # Set the valve to the initial port
    port = input("Type the number port your capillary is screwed into (e.g. 6)\n")
    setport = '/1B' + port + 'R\r'
    lsp.write(setport.encode())
    while 1:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('ASCII')
            if key == 'a':
                if (position + stepsize) * 8 < 10000:
                    pickup()
                    print (" pickup " + str(pic_volume) + "nl, current volume: " + str(position * 8) + "nl")
                else:
                    print('This is beyond the maximum volume. Please reconsider')
            if key == 'c':
                if position > 0:
                    print ("dispense " + str(position * 8) + "nl")
                    dispense()
                    print ("syringe position: " + str(position))
                else:
                    print('You cannot dispense 0nl')
            if key == 'v':
                change_volume()
            if key == 'i':
                initialize()
            if key == 'f':
                fill_tube() # fill from valve 1 to valve 2 with 15 times 20 µl (300 µl)
            if key == 'l':
                clean_tube() # fill from valve 1 to valve 2 with 5 times 20 µl (100 µl)
            if key == 'p':
                push_out_100() # push out 100 nl from reservoir
            if key == 't':
                change_port()
            if key == 'h':
                print(helpText)
            if key == 'q':
                exit()

####### Legacy code commented out of the original script

#def inkey():
#        fd=sys.stdin.fileno()
#        remember_attributes=termios.tcgetattr(fd)
#        tty.setraw(sys.stdin.fileno())
#        character=sys.stdin.read(inkey_buffer)
#        termios.tcsetattr(fd,termios.TCSADRAIN, remember_attributes)
#
#        return character

#initial setting of stepsize and valve sequence
##    examples:
##    lsp.write(b"/1P10R\r") pickup 10 steps = 80nl
##    lsp.write(b"/1D10R\r") dispense 10 steps = 80nl
