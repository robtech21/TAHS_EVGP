# Hacked together data monitor rehash for meshtastic
# Written by Robert Furr
# NOTE This is meant for Windows, not Linux.

import serial,io,csv,time,meshtastic
from pubsub import pub
import serial.tools.list_ports as list_ports
from meshtastic.serial_interface import SerialInterface
from random import randint
from time import sleep
from os import name,system
from sys import argv

def get_current_time():
    current_time = str(time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime()))
    return current_time

# Only import winsound on Windows
if name == "nt":
    import winsound

SerialException = serial.serialutil.SerialException

# Set basic serial config
Port = "/dev/ttyUSB0" # Default Unix port

if name == "nt":
    # Switch to COM1 if windows
    Port = "COM1"
Baud = 9600

# Argument values
debug        = False
nodetect     = False
nosound      = False
auto_port    = False
auto_baud    = False

Name=None

# Process arguments

if "help" in argv:
    print('''
Arguments list:
nodetect - Disables detecting ports
nosound - Disables the sound functionality

Config arguments:
port - Sets your port
baud - Changes the usually hardcoded baudrate
name - Sets the file subject, no subject will just leave a filename with a date
example: data_monitor_mesh.py port=COM6 baud=9600
''')

    exit(0)

for arg in argv:

    if "nodetect" in arg:
        nodetect = True
        print("Not detecting ports")
    if "nosound" in arg:
        nosound = True
        print("Disabled sound")
    if "debug" in arg:
        debug = True
        print("Debug enabled")

    try:
        arg = arg.split("=")
        if arg[0] == "port":
            Port = arg[1]
        if arg[0] == "baud":
            Baud = arg[1]
        if arg[0] == "name":
            Name = arg[1]
    except IndexError:
        pass

def clr():
    # Clear function for wiping the screen
    if name == "nt":
        system("cls")
    else:
        try:
            system("clear")
        except Exception as e:
            print(e)
            pass

def beep(freq,duration):
    # Sound for Windows-only
    if name == "nt":
        winsound.Beep(freq,duration)

def alarm(level=1,time=500):
    # Alarm beeper based on a "level" system
    tone1 = level*100
    tone2 = round(level*100/2) # Round because beep() doesn't take float values
    beep(tone1,time)
    beep(tone2,time)

def rand():
    # Random number
    num = float(randint(1,24))
    return num

def write_csv(file_name,data,type='w'):
    with open(file=file_name,mode=str(type),newline='\n') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

# Startup
clr()
alarm()
print("Cycle Analyst Data Monitor - For Meshtastic Use\nCreated by Robert Furr\n\nRunning config...")
print("Hardware config:")

# Serial Config

Timeout = 10
ser = serial.Serial()

if name == "nt":
    # Get system COM ports on Windows
    ports_list = list_ports.comports()
    try:
        # Check for 'nodetect' argument 
        if nodetect == False:
            # Select first port in list as default
            format_port_list = []
            print("Connected Ports:")
            for e in ports_list:
                # List out ports
                print(str(e))
                format_port_list.append(str(e).split(" ")[0])
            Port = format_port_list[0]
                    
    except IndexError:
        # Exit with error code 1 if no ports
        print("No ports on your system! Exiting.")
        exit(1)

    new_port = input("Select port (leave empty for default "+str(Port)+")\n> ")
    if new_port != "":
        Port = new_port

ser = SerialInterface(Port)
print("Serial initialized")

# CSV config
fields = ["Sec","Ah","V","A","S","D","Deg","RPM","HW","Nm","ThI","ThO","Acc","Lim"]
if Name == None:
    Name = ""
filename = str("ev_data/"+get_current_time()+"_"+str(Name)+".csv")
temp_filename = "ev_data/temp.csv"

print("CSV configured\nFile Topic: "+str(Name)+"\nFile: "+str(filename)+"\n")

# Write fields for both files
write_csv(temp_filename,fields)
write_csv(filename,fields)

count = 0
def onReceive(packet,interface):
    # Attempt to decode received message
    global count
    try:
        data = packet.get('decoded').get('payload')
        Data = data.decode().split("\t")
        #Data[13] = 0
        write_csv(filename,Data,'a') # Write master file
        write_csv(temp_filename,Data,'a') # Write temp file for data monitor program
        count += 1
        print(data)
        if count == 20:
            #write_csv(temp_filename,fields) # Clear temp CSV and re-add headers
            #write_csv(temp_filename,data,'a')
            count = 0
    except Exception as e:
        print(e)
        pass

pub.subscribe(onReceive, "meshtastic.receive.data")
ser.sendText("Rx Open "+str(int(rand()))) # Random number helps distinguish it from previous init message
print("Subscription started. You should start receiving messages soon.")

while True:
    try:
        sleep(1) # Mindless loop to keep program running
    except KeyboardInterrupt:
        print("Exit") # Clean exit
        exit(0)