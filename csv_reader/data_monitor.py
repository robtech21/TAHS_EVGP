import serial,io,csv,time
from random import randint
from time import sleep
from os import name,system

# Amount of rows before the header prints again
before_clear = 40

# Feeds the system randomly generated data
debug = True

def clr():
    # Clear function for wiping the screen
    if name == "nt":
        system("cls")
    else:
        system("clear")

# Sample data for debugging and testing
testdata = "0.0000	47.42	0.0	0.00	0.0000"
testdata2 = bytes(b'0.0000\t58.77\t0.0\t0.00\t0.0000\r\r\n')
clr()

if name == "nt":
    Port = "COM1"
else:
    if debug == True:
        Port = "/dev/ttyS0" # For my personal machine
    else:
        Port = "/dev/ttyUSB0"

ser = serial.Serial()
ser.timeout = 2

while True:
    choice = input('''Your default port is: '''+str(Port)+'''
Leave blank for default or type your port and press enter to continue
port> ''') # Serial port selection
    if choice == "":
        print("Proceeding with default port "+str(Port))
        break
    else:
        Port = choice
        break
    clr()
print("Setting port")
ser.port = Port
print("Port set")

while True:
    choice = input('''Leave blank for default baud of 9600 or type your baud rate and press enter
baud> ''')
    if choice == "":
        Baud = 9600
        break
    else:
        Baud = int(choice)
        break
    clr()
print("Setting baud")
ser.baudrate = Baud
print("Baud rate is now "+str(Baud))

def shutdown(error=0):
    print("\nClosing serial...")
    ser.close()
    print("Closed serial")
    print("Exit with code "+str(error))
    exit(error)

print("Opening serial communication...")
ser.open()
print("Opened serial\n")
clr()
print ('\nStatus: ',ser)

clear_table = 0
header = "Sec\tAh\tV\tA\tS\tD"

fields = ["Sec","Ah","V","A","S","D"]
filename = "../ev_data/car_data.csv"

with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)

data = ser.readline().decode()
print(header)
start_time = time.time()

while True:
    try:
        if debug == True:
            sleep(0.2)
            data = testdata2.decode()
        else:
            data = ser.readline().decode().replace("\n","")
        currentsec = time.time()-start_time
        data = str(round(currentsec,2))+"\t"+ data # Format time into the chart
        print(data)
        csvdata = data.replace("\t"," ").replace("\r","").replace("\n","").split(" ") # Prepare data for writing into a CSV file

        if debug == True:
            csvdata[2] = str(float(csvdata[2])+randint(0,10)) # Create variations in the data for debug testing
            csvdata[1] = str(float(csvdata[1])+randint(5,21))
            print(csvdata)
        for i in range(len(csvdata)):
            csvdata[i] = str(round(float(csvdata[i]),2))
        #print(csvdata)
        clear_table = clear_table + 1
        if clear_table == before_clear:
            #clr()
            print(header)
            clear_table = 0

        row = csvdata
        with open(filename, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(row) # Write to opened CSV file

    except KeyboardInterrupt:
        shutdown()
