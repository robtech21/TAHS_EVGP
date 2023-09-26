import serial,io,csv,time
import serial.tools.list_ports as list_ports
from random import randint
from time import sleep
from os import name,system
from sys import argv

# Only import winsound on Windows
if name == "nt":
    import winsound

SerialException = serial.serialutil.SerialException

# Argument values
debug       = False
nodetect    = False
nosound     = False
autoconfig  = False

# Process arguments
for arg in argv:
    if "nodetect" in arg:
        nodetect = True
    if "nosound" in arg:
        nosound = True
    if "debug" in arg:
        debug = True
    if "autoconfig" in arg:
        autoconfig = True
        arg = arg.split("!")
        try:
            Port    = arg[1]
            Baud    = arg[2]
        except IndexError:
            pass

def get_current_time():
    current_time = str(time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime()))
    return current_time

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

# Startup
clr()
alarm()
print("Cycle Analyst Data Monitor\nCreated by Robert Furr\n\nRunning config...\nAutoconfig: "+str(autoconfig))

# Serial Config
Port = "/dev/ttyUSB0" # Default Unix port

if name == "nt":
    # Switch to COM1 if windows
    Port = "COM1"
Baud = 9600
Timeout = 10
ser = serial.Serial()

if autoconfig == False:
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

# CSV config
fields = ["Sec","Ah","V","A","S","D","Deg","RPM","HW","Nm","ThI","ThO","Acc","Lim"]
filename = "ev_data/car_data_master.csv"
temp_filename = "ev_data/temp.csv"

# Serial variable and settings
ser.port = Port
ser.timeout = Timeout
ser.baudrate = Baud

print("Config finished.\n")

with open(filename, 'w',newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
with open(temp_filename, 'w',newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)

# Counters for serial errors
sec_count = 0
count = 1

# Open serial comm
while True:
    if debug == True:
        print("Debug")
        break
    try:
        sleep(sec_count)
        print("Opening serial communication on port "+str(Port)+" (Try "+str(count)+")")
        ser.open()
        print("Opened serial in "+str(count)+" tries\n")
        print ('Status: \n'+str(ser))
        break
    except KeyboardInterrupt:
        exit(0)
    except SerialException as e:
        try:
            # Retry connection
            if sec_count < 5:
                sec_count = sec_count + 1
            count = count + 1
        
            beep(600,500)
            if count >= 10:
                beep(800,500)
                print("Connection re-tried "+str(count-1)+" times. Something is wrong!")
            print("Connection Error: "+str(e)+"\nRetrying in "+str(sec_count)+" seconds\n")
        except KeyboardInterrupt:
            exit(0)
        pass

# Get start time for 'sec' data point
start_time = time.time()
count = 0
no_go = False
while True:
    try:
        # Main loop
        Data = ""
        writelist = [] # Reset write list
        currentsec = round(time.time()-start_time,2) # Get current time and append it onto the write list
        if debug != True:
            try:
                Data = ser.readline().decode() # Read data and decode it into a string
            except Exception as e:
                print("Err, not sending string")
                no_go = True
            no_go = False
            writelist.append(currentsec)
            data_new = Data.split("\t") # Split data by tab character
            #print("Data: \n"+str(Data))
            #print("Decoded data: \n"+str(data_new))
            for e in data_new:
                writelist.append(e) # Individually append each item onto the list to be written

        # Emulates most/all the 14 data points provided by the CA
        if debug == True:
            writelist = [currentsec,rand(),rand(),rand(),rand(),rand(),rand(),rand(),rand(),rand(),rand(),rand(),rand(),0.00]
        # Write to both master and temp file
        if Data == "":
            no_go = True
        if no_go == False:
            if len(writelist) == 15:
                writelist.pop(14)
                with open(filename, 'a',newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(writelist) # Write master CSV
                with open(temp_filename, 'a',newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(writelist) # Write temp CSV
                count = count + 1
            for item in writelist:
                print(item,end=" ")

        if count == 20:
            with open(temp_filename, 'w',newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(fields)
            count = 0
        sleep(0.2)

    except Exception as e:
        # Crash code
        print("Program encountered an error\n"+str(e))
        exit(1)

    except KeyboardInterrupt:
        print("Exit")
        exit(0)