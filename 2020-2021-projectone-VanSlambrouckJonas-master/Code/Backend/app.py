#!/usr/bin/env python3
import wiimote
import sys

#gps
import serial

#OLED
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

#api/socket
from logging import lastResort
import time
import math
import threading
import multiprocessing as mp
import datetime
import json
import os
from RPi import GPIO
from flask_cors import CORS
from flask_socketio import SocketIO, disconnect, emit, send
from flask import Flask, jsonify, request
from reposetories.DataRepository import DataRepository
from helpers.klasseAnalog import ANALOG


#------------------------------------------------hardware------------------------------------------------
tracking = 1

# Wiimote
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.HIGH)
pwm = GPIO.PWM(12, 50) 


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

disp.fill(0)
disp.show()

width = disp.width
height = disp.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), outline=0, fill=0)
padding = -2
top = padding
bottom = height - padding
x = 0
font = ImageFont.load_default()
    

draw.rectangle((0, 0, width, height), outline=0, fill=0)
cmd = "hostname -I | cut -d' ' -f1"
IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = 'cut -f 1 -d " " /proc/loadavg'
CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")

draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
draw.text((x, top + 14), "CPU load: " + CPU, font=font, fill=255)
draw.text((x, top + 28), MemUsage, font=font, fill=255)
draw.text((x, top + 42), "HomePage.html", font=font, fill=255)

disp.image(image)
disp.show()
time.sleep(0.1)


# GPS
def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.7f" %(position)
    return position

#------------------------------------------------Flask------------------------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app)

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)

#------------------------------------------------threading------------------------------------------------
def readvoltage(): 
    gpgga_info = "$GNGGA,"
    ser = serial.Serial ("/dev/serial0", timeout=1)              #Open port with baud rate
    GPGGA_buffer = 0
    NMEA_buff = 0
    lat_in_degrees = 0
    long_in_degrees = 0
    lat = 0
    longi = 0
    while True:
        idsession = DataRepository.read_last_sessionid()[0]['sessionID']
        print("session: ", idsession)
        print("-----")
        if tracking != 0:
            received_data = (str)(ser.readline())
            #print(received_data)                   #read NMEA string received
            GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string    
            print(GPGGA_data_available)

            lowestdata = float(ANALOG().read_channel(int(6)))
            print("lowestdata: ", lowestdata)
            if lowestdata >= 0:
                print("session: ",idsession)
                databattery = DataRepository.create_event(idsession, 4, lowestdata, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                print(databattery)

            if (GPGGA_data_available > 0):
                print(received_data)
                GPGGA_buffer = received_data.split("$GNGGA,",1)[1]  #store data coming after "$GPGGA," string 
                NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
                nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
                nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
                nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
                amount_satelites = NMEA_buff[6]
                altitude = NMEA_buff[8]
                
                if nmea_longitude:
                    print("NMEA Time: ", nmea_time,'\n')
                    print ("NMEA Latitude:", nmea_latitude,"NMEA Longitude:", nmea_longitude,'\n')
                    print("Amount of satelites: ", amount_satelites)
                    
                    lat = float(nmea_latitude)                  #convert string into float for calculation
                    longi = float(nmea_longitude)               #convertr string into float for calculation
                    

                    decimal_value = lat/100.00
                    degrees = int(decimal_value)
                    mm_mmmm = (decimal_value - int(decimal_value))/0.6
                    position = degrees + mm_mmmm
                    lat_in_degrees = "%.7f" %(position)

                    decimal_value = longi/100.00
                    degrees = int(decimal_value)
                    mm_mmmm = (decimal_value - int(decimal_value))/0.6
                    position = degrees + mm_mmmm
                    long_in_degrees = "%.7f" %(position)
                    
                    print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')
                    dataLAT = DataRepository.create_event(idsession, 1, lat_in_degrees, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    dataLONG = DataRepository.create_event(idsession, 2, long_in_degrees, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    dataALT = DataRepository.create_event(idsession, 3, altitude, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    print(lat_in_degrees)
                    print(long_in_degrees)
                    print(altitude)

        status = DataRepository.read_voltage(1)
        socketio.emit('B2F_pecentage', {'data': status}, broadcast=True)
        time.sleep(5)

def remote():
    time.sleep(10)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'cut -f 1 -d " " /proc/loadavg'
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")

    draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
    draw.text((x, top + 14), "CPU load: " + CPU, font=font, fill=255)
    draw.text((x, top + 28), MemUsage, font=font, fill=255)
    draw.text((x, top + 42), "HomePage.html", font=font, fill=255)
    draw.text((x, top + 56), "press 1 +2 to connect", font=font, fill=255)

    disp.image(image)
    disp.show()
    time.sleep(0.1)

    print("Press the 'sync' button on the back of your Wiimote Plus " +
      "or buttons (1) and (2) on your classic Wiimote.\n" +
      "Press <return> once the Wiimote's LEDs start blinking.")

    if len(sys.argv) == 1:
        addr, name = wiimote.find()[0]
    elif len(sys.argv) == 2:
        addr = sys.argv[1]
        name = None
    elif len(sys.argv) == 3:
        addr, name = sys.argv[1:3]        
    
    print(("Connecting to %s (%s)" % (name, addr)))
    wm = wiimote.connect(addr, name)

    # Demo Time!
    patterns = [[1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [1, 0, 0, 0]]
    for i in range(5):
        for p in patterns:
            wm.leds = p
            time.sleep(0.05)


    def print_ir(ir_data):
        if len(ir_data) == 0:
            return
        for ir_obj in ir_data:
            # print("%4d %4d %2d     " % (ir_obj["x"],ir_obj["y"],ir_obj["size"]), end=' ')
            print("%4d %4d %2d     " % (ir_obj["x"], ir_obj["y"], ir_obj["size"]))
        print()

    disp.image(image)
    disp.show()
    time.sleep(0.1)


    #wm.ir.register_callback(print_ir)


    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'cut -f 1 -d " " /proc/loadavg'
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")

    draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
    draw.text((x, top + 14), "CPU load: " + CPU, font=font, fill=255)
    draw.text((x, top + 28), MemUsage, font=font, fill=255)
    draw.text((x, top + 42), "HomePage.html", font=font, fill=255)
    draw.text((x, top + 56), "connectd :)", font=font, fill=255)

    disp.image(image)
    disp.show()
    time.sleep(0.1)


    dc=15
    pwm.start(dc) 
    while True:
        if wm.buttons["Up"] & wm.buttons["B"]:
            dc += 0.1
            if dc > 20:
                dc = 20
            pwm.ChangeDutyCycle(dc)
            print("btn UP       " + str(dc))
            time.sleep(0.2)
        elif wm.buttons["Down"] & wm.buttons["B"]:
            dc -= 0.1
            if dc < 10:
                dc = 10 
            pwm.ChangeDutyCycle(dc)
            print("btn Down     " + str(dc))
            time.sleep(0.2)
        elif wm.buttons["Plus"] & wm.buttons["Minus"]:
            os.system("sudo shutdown -h now")
        elif wm.buttons["B"]:
            idsession = DataRepository.read_last_sessionid()[0]['sessionID']
            speed = DataRepository.create_event(idsession, 5, (dc - 15) / 5 * 100, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print("B")
            time.sleep(0.2)
        else:
            idsession = DataRepository.read_last_sessionid()[0]['sessionID']
            if dc < 14.9:
                dc += 0.1
                pwm.ChangeDutyCycle(dc)
                print("UP     " + str(dc))
                speed = DataRepository.create_event(idsession, 5, (dc - 15) / 5 * 100, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            elif dc > 15.1:
                dc -= 0.1
                pwm.ChangeDutyCycle(dc)
                print("Down     " + str(dc))
                speed = DataRepository.create_event(idsession, 5, (dc - 15) / 5 * 100, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(0.01)

def readbtn():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)
    GPIO.setup(16, GPIO.IN)
    GPIO.add_event_detect(16, GPIO.RISING, bouncetime=1000)

    GPIO.output(21, GPIO.HIGH)
    while True:
        if GPIO.event_detected(16) and tracking == 1:
            global id
            print('Edge detected on channel', 16)
            if GPIO.input(20) == 1:
                GPIO.output(20, GPIO.LOW)
                sessionid = DataRepository.read_last_sessionid()[0]['sessionID']
                
                speed = DataRepository.read_speed(sessionid)

                first = DataRepository.read_get_first(sessionid)
                last = DataRepository.read_get_last(sessionid)
                if len(first) == 2 and len(last) == 2 and first != last:
                    R = 6373.0
                    lat1 = math.radians(first[0]['value'])
                    lon1 = math.radians(first[1]['value'])
                    lat2 = math.radians(last[1]['value'])
                    lon2 = math.radians(last[0]['value'])
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1
                    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                    distance = round((R * c), 3)
                    print("distance: ", distance)                    
                else:
                    distance = 0
                
                if len(speed) > 0:
                    avgspeed = speed[0]['avg']
                    maxspeed = speed[0]['max']
                    print("maxspeed: ", maxspeed, "     avgspeed: ", avgspeed)
                else:
                    avgspeed = 0
                    maxspeed = 0


                session = DataRepository.update_session(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), maxspeed, avgspeed, distance, sessionid)
                print("OFF")
            else:
                GPIO.output(20, GPIO.HIGH)
                idsession = DataRepository.read_last_sessionid()[0]['sessionID']
                print("session: " ,idsession)
                id = idsession + 1
                print("new session: ", id)
                session = DataRepository.create_session(1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                print("ON")

thread = threading.Thread(target=readvoltage)
thread.start()
threadRemote = threading.Thread(target=remote)
threadRemote.start()
threadbtn = threading.Thread(target=readbtn)
threadbtn.start()

print("**** Program started ****")


#------------------------------------------------API------------------------------------------------
# API ENDPOINTS
endpoint = '/api/v1'


@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # # Send to the client!
    # vraag de status op van de lampen uit de DB
    status = DataRepository.read_last_gps()
    socketio.emit('B2F_currentgps', {'data': status}, broadcast=True)
    status = DataRepository.read_voltage(1)
    socketio.emit('B2F_pecentage', {'data': status}, broadcast=True)
    status = DataRepository.read_current_voltage()
    socketio.emit('B2F_currentVoltage', {'data': status}, broadcast=True)
    status = DataRepository.read_basic_stats()
    socketio.emit('B2F_basicStats', {'data': status}, broadcast=True)
    status = DataRepository.read_ride(17)
    socketio.emit('B2F_ride', {'data': status}, broadcast=True)
    status = DataRepository.read_all_rides()
    socketio.emit('B2F_AllRides', {'data': status}, broadcast=True)

@socketio.on('F2B_get_ridedata')
def addProgress(id):
    status = DataRepository.read_ride(id)
    socketio.emit('B2F_ride', {'data': status}, broadcast=True)

@socketio.on('F2B_power_off')
def addProgress():
    print("powering off raspberry pi")
    os.system("sudo shutdown -h now")

# ANDERE FUNCTIES


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
