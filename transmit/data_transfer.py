#!/usr/bin/env python3

# EVGP data transmission and local logging program
# Written by Robert Furr
# This is incredibly janky, but it should work ok :)

# NOTE: Meant to run on a Raspberry Pi, but should work on any Linux system
# Due to neopixels being used, this program MUST be run as root on RPi (sorry)

import serial,time,os,csv,sys,subprocess,meshtastic,random
import subprocess as sp
from os import system
from meshtastic.serial_interface import SerialInterface
from sys import argv
from time import sleep
SerialException = serial.serialutil.SerialException

# Mesh config
Mesh  = True # Use mesh device (setting to False uses serial device)
log_mesh = True # Log to mesh or not
mesh_ID = 3667826704 # ID of the receiver node (important when used with a repeater)
do_ack = False # Acknowledgement is off by default for low latency (with the exception of error logging)
freq = 2 # Frequency of transmitting data over mesh (default: 2)

# Misc. settings
use_pin = True # Use Raspberry Pi GPIO/Neopixel
reboot_override = False # If true, it will always reboot the system if err() is called

# Device configuration
tx = ["/dev/ttyACM0",9600] # ACM0 is the default port name of most Arduino Uno R3 boards (and some Meshtastic devices)
rx = ["/dev/ttyUSB0",9600] # USB0 is usually the assigned device for the CA data programming cable
dev = ["/dev/sda1","/mnt/csv_out/"] # USB drive location and mount point for external USB data writing
ext = False # External USB data logging
original_directory = "/home/pi/csv_out/" # Original data out directory, changed to dev[1] if ext is True
directory = original_directory
print("Data Analytics Transmit Program\nWritten by Robert Furr\n2023\n")

if "help" in argv:
        print('''Possible Arguments:
dummytest - For fake CA-V3 testing
extdrive  - Enables external USB drive writing (Pi only)
reboot    - The program will reboot instead of exiting if enough errors are caught''')
        exit(0)

if "dummytest" in argv: # For my CA V3 "emulator" that I use for testing
        rx = ["/dev/ttyACM1",9600]

if "extdrive" in argv:
        ext = True

if "reboot" in argv:
        reboot_override = True

if sys.platform != "linux": # Keep non-Linux users out
        print("Non-Linux system detected, closing with error code 1.")
        exit(1)

def get_current_time(no_date=False):
        # Gets the formatted time formatted as Y-M-D_H-M-S or H-M-S
        current_time = str(time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime()))
        if no_date == True:
                current_time = current_time.split("_")[1]
        return current_time

print("Program started "+get_current_time())
if argv[0] != "":
        print("Args:")
        for arg in argv:
                print(str(arg))
        print()

def umount():
        if ext:
                try: # Tries to unmount the USB drive
                        subprocess.run(["sudo","umount",dev[0]])
                        print("Drive unmounted")
                except Exception as e:
                        print(e)
                        print("Drive unmount fail")
                        pass

print("Program started "+get_current_time())
setup_err = 0
try:    
        # Import and configure GPIO
        import board,neopixel
        import RPi.GPIO as GPIO

        # Shorthands for GPIO functions (deprecated)
        setup = GPIO.setup
        OUT = GPIO.OUT
        HIGH = GPIO.HIGH
        LOW = GPIO.LOW
        pinOut = GPIO.output
        GPIO.setmode(GPIO.BCM)
        pixels = neopixel.NeoPixel(board.D18,4)
        pixels.brightness = 0.1
        
        # Pin config
        ON = 0
        ERR = 3
        ACT = 2
        pixels[ON] = (255,0,0)

except RuntimeError:
        # Disable GPIO actions entirely if not on RPI
        print("Not a Raspberry Pi or you didn't run the program with sudo")
        use_pin = False
        setup_err += 1
except ModuleNotFoundError:
        print("Neopixel or RPi GPIO module not found")
        use_pin = False
        setup_err += 1
if use_pin == False:
        print("Disabling GPIO")
        ON = 0
        ERR = 2

def flash(amount=1,pin=ERR,delay=0.5):
        # Toggle pin on and off for LEDs, intended for error codes
        if use_pin:
                for i in range(0,amount):
                        #pinOut(int(pin),HIGH)
                        pixels[pin] = (0,255,0)
                        #print("On")
                        sleep(delay)
                        #pinOut(pin,LOW)
                        #print("Off")
                        pixels[pin] = (0,0,0)
                        if i != amount-1: # Gets rid of unneeded delay at end
                                sleep(delay)
transmit_ser=False
# Connect to meshtastic
if Mesh:
        try:
                ser3 = SerialInterface(tx[0])
                ser3.sendText("Init transmitter at "+str(":".join(get_current_time(no_date=True).split("-"))),destinationId=mesh_ID,wantAck=True)
                sleep(0.5)
        except FileNotFoundError: # Fall back onto serial for redundancy
                print("Can't connect to mesh device, not plugged in?\nFalling back on serial.")
                Mesh = False
                transmit_ser=True
                setup_err += 1

if ext:
        # Try mounting the drive
        print("Mount drive")
        result = system("sudo mount "+str(dev[0])+" "+str(dev[1]))
        directory=dev[1]#+"data_out/"
        if str(result) != "0":
                print("Somehow failed to mount "+dev[0]+" ("+str(result)+")\nFallback to default directory")
                directory = original_directory
                ext = False
                setup_err += 1

print()

def log(text,added_text="",error=False,ack=do_ack):
        # Logging function with the ability to log to mesh
        print(str(text))
        if error:
                ack = True # Turn on ack for errors only
        if Mesh and log_mesh:
                ser3.sendText(str(text)+str(added_text),wantAck=ack,destinationId=mesh_ID)
        if error:
                flash()
                if Mesh:
                        sleep(0.8) # Error string is likely quite long, give a bit of a delay before resuming.
        sleep(0.2)

def err(code=1):
        # Reboots the system
        if use_pin:
                #flash(5,delay=0.2)
                pixels[ON] = (255,255,0)
                pixels[ERR] = (0,255,0)
        if ext:
                umount()
        if Mesh:
                ser3.sendText("Rebooting with code "+str(code),destinationId=mesh_ID,wantAck=True)
                ser3.close()
        print("Too many errors caught, rebooting system with code "+str(code))
        try:
                subprocess.run(["chmod", "-R", "a+rwX", "csv_out/"])
        except Exception as e:
                print(e)
                pass
        if reboot_override:
                system("sudo reboot")
        else:
                exit(1)

# Serial config and connection
conn_tries = 1 # Amount of tries
max_conn = 5 # Maximum tries
while True:
        try:
                # Port 1 (recieve) config
                log("Config "+str(rx[0])+" ("+str(conn_tries)+")")
                ser1 = serial.Serial(port=rx[0],
                        baudrate=rx[1],
                        timeout=None
                        )
                sleep(0.2)
                # Open ports
                log("Opening "+str(rx[0])+" ("+str(conn_tries)+")")
                if ser1.is_open == False:
                        ser1.open()
                else:
                        log("Receiver already opened")
                conn_tries = 1

                # Port 2 (transmit) config
                if Mesh == False: # Attempt to register transmit device if meshtastic is disabled
                        try:
                                print("Opening "+str(tx[0])+" ("+str(conn_tries)+")")
                                conn_tries = 1
                                ser2 = serial.Serial(
                                        port=tx[0],
                                        baudrate=tx[1],
                                        timeout=None,
                                        )
                                if ser2.is_open == False:
                                        ser2.open()
                                else:
                                        print("Transmitter already opened")
                        except SerialException as e:
                                print(e)
                                print("Fallback to no transmission (local storage only)")
                                transmit_ser = False # Fallback to local storage

                conn_tries = 1
                break # Break out of loop to open main loop
        except SerialException as e:
                # Error code
                flash()
                log(e,added_text=" ("+str(conn_tries)+")",error=True)
                conn_tries += 1
                setup_err += 1
                if conn_tries > max_conn:
                        # Activate reboot when maximum retries reached
                        err()
                sleep(2)
                pass

time=get_current_time() # Integrating get_current_time() into the filename variable creates problems
filename = directory+time+".csv" # Create filenames

field_names = ["Sec","Ah","V","A","S","D","Deg","RPM","HW","Nm","ThI","ThO",'Acc',"Lim"] # CSV headers
log("Filename: "+str(filename))

if "list" in argv:
        itemlist=[]
        print("\nFile List:\n")
        dirlist = os.listdir(directory)
        for item in dirlist:
                e = item.split("_")
                e[0]=e[0].replace("-",".")
                e[1]=e[1].replace("-",":").replace(".csv","")
                itemlist.append(str(item+" \t "+e[0]+" at "+e[1]))
        itemlist.sort()
        for i in itemlist:
                print(i)
        print("\nExiting")
        exit(0)

with open(filename,'w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(field_names)

data_counter = 0
err_count = 0
max_err = 5
counter=0
seldata = 0
log("Setup ran with "+str(setup_err)+" error(s)!\n")
sleep(1)
# Main loop
while True:
        try:
                # Get data and write to other serial device
                original_data = ser1.readline()
                if original_data.decode() != 0:
                        data = original_data.decode().split("\t") # Decode data and split
                        counter+=1 # Increment counter
                        data[0] = str(counter)
                        data[2] = str(seldata+random.randint(-2,2)) # Debug, pls remove for final version
                        data[13] = data[13].replace("\r\n","") # Fix weird bug where it writes a single `"` character on a newline in CSV
                        data = "\t".join(data).encode() # Join and re-encode data

                        # Transmit data over mesh device or serial
                        if Mesh:
                                data_counter = (data_counter+1)%int(freq)
                                if data_counter==0:
                                        seldata = random.randint(10,24) # Also debug
                                        if use_pin:
                                                pixels[ACT] = (255,255,0)
                                        ser3.sendData(data)
                                        if use_pin:
                                                pixels[ACT] = (0,0,0)
                        if transmit_ser:
                                ser2.write(data)
                        
                                
                        # Write data to local CSV file
                        print(data)
                        csv_data = data.decode().split("\t") # Decode the tab seperated data, split it, and write to CSV
                        with open(filename,'a',newline='\n') as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow(csv_data) 
                                if use_pin: # Change perms only on RPi
                                        subprocess.run(["sudo", "chmod", "-R", "a+rwX", directory])

        except KeyboardInterrupt:
                if ext:
                        umount()
                print("\nClean exit")
                exit(0)
        except IndexError:
                pass
        except Exception as e:
                log(e,error=True)
                err_count += 1
                if err_count == max_err:
                        # Reboot system or kill program
                        err()
