#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 16:37:51 2018

@author: lspone
"""
import time
import serial

#connect pump
#lsp = serial.Serial('/dev/cu.usbserial-LSP18082_0RL102', 9600, timeout=10)
lsp = serial.Serial('COM4', 9600, timeout=10)

#initialize pump
lsp.write(b"/1ZR\r")

#initial setting of stepsize and valve sequence
    #examples
    #lsp.write(b"/1P10R\r") pickup 10 steps = 80nl
    #lsp.write(b"/1D10R\r") dispense 10 steps = 80nl

stepsize = int(input("Choose initial pickup volume per pedal strike: 1 = 8 nl\n"))
pic_volume = stepsize * 8
print ("Pickup volume is: ", pic_volume, "nl\ndispension is always total volume\nchange pickup volume with key v\nexit program with key q\n\nleft pedal - pickup\nright pedal - dispense")

position = 0
lsp.write(b'/1B2R\r')

def initialize():
    global posisiton
    lsp.write(b'/1ZB2R\r')
    position = 0

def push_out_100():
    lsp.write(b'/1gB1P120B2D120R\r')
    
def change_volume():
    global stepsize
    global pic_volume
    stepsize = int(input("Choose pickup volume per pedal strike: 1 = 8 nl\n"))
    pic_volume = stepsize * 8
    print ("Pickup volume is: ", pic_volume, "nl")
    return stepsize, pic_volume

pic = ""
dis = ""

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
    print (pic)
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
    d = str(position)
    d1 = "/1D" + d + "R\r"
    dis = d1.encode()
    print (dis)
    lsp.write(dis)
    position = position - position
    return dis, position


    
import sys
#import termios
#import tty
from pynput import keyboard
import os
import msvcrt
inkey_buffer = 1

#def inkey():
#        fd=sys.stdin.fileno()
#        remember_attributes=termios.tcgetattr(fd)
#        tty.setraw(sys.stdin.fileno())
#        character=sys.stdin.read(inkey_buffer)
#        termios.tcsetattr(fd,termios.TCSADRAIN, remember_attributes)
#        
#        return character
    
while 1:
    #key = (inkey())
    if msvcrt.kbhit():
        key = msvcrt.getch().decode('ASCII')
           
        if key == 'a':
            pickup()
            print (" pickup " + str(pic_volume) + "nl, current volume: " + str(position * 8) + "nl")
                
        if key == 'c':
            print ("dispense " + str(position * 8) + "nl")
            dispense()
            print ("syringe position: " + str(position))

        if key == 'v':
            change_volume()
               
        if key == 'i':
            initialize()

        if key == 'f':
            fill_tube() #fill from valve 1 to valve 2 with 15 times 20 µl (300 µl)

        if key == 'c':
            clean_tube()#fill from valve 1 to valve 2 with 5 times 20 µl (100 µl)

        if key == 'p':
            push_out_100()#push out 100 nl from reservoir

        if key == 'q':
            exit()
            




