"""
This Code belongs to SME Dehraun. For any query write to schematicslab@gmail.com
"""

import BlynkLib
from BlynkTimer import BlynkTimer
import serial
from datetime import datetime
import sqlite3
from time import sleep
import signal                   
import sys
import RPi.GPIO as GPIO

conn = sqlite3.connect('iot_data.db')
c = conn.cursor()

#Create table sensor Data
c.execute('''
CREATE TABLE IF NOT EXISTS sensor_data (
    GAS INT,
    TEMP INT,
    SMOKE INT,
    TEMP_sys INT,
    DEVICE TEXT,
    DATE TEXT,
    TIME TEXT
)
''')

BUTTON_GPIO = 16
LED_GPIO = 19
BLYNK_AUTH_TOKEN = 'xnWepqN6sHxDLgZJLSOpvuTU9KMmMe1C'
#BLYNK_AUTH_TOKEN_1 = 'IUd0LdtwsV2laOCcIMK672bx4KR74G0q'

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)
# blynk1 = BlynkLib.Blynk(BLYNK_AUTH_TOKEN_1)

led_state = True

# Create BlynkTimer Instance
timer = BlynkTimer()
ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def button_callback(channel):
    if GPIO.input(BUTTON_GPIO):  # Kiểm tra nút nhấn
        global led_state
        led_state = not led_state
        if led_state == True:
            ser.write(str('8').encode())
            ser.flush()
            print("ON")
        else:
            ser.write(str('9').encode())
            ser.flush()
            print("OFF")

# Function to sync the data from virtual pins
@blynk.on("connected")
def blynk_connected():
    print("Fire!!!!!!!!!!!!")
    print(".......................................................")
    print("................... By HIEU IOT ...................")
    sleep(2)

# LED control through V4 virtual pin
@blynk.on("V4")
def v0_write_handler(value):
    if int(value[0]) != 0:
        ser.write(str('8').encode())
        ser.flush()
        print("ON")
    else:
        ser.write(str('9').encode())
        ser.flush()
        print("OFF")

def receive_data():
    try:
        print("Đang chờ nhận dữ liệu từ ...")
        while True:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")
            ser.write(str('1').encode())  # Gửi tín hiệu 'READY' tới STM32 để báo rằng Pi đã sẵn sàng
            ser.flush()
            if ser.in_waiting > 0:
                try:
                    received_data = ser.readline().decode().strip()
                    field1, field2 , field3, field4 = map(int, received_data.split(','))
                    print("Node 1:")
                    print(f"Gas={field1},Smoke ={field2} ,Temp_sys={field3}, Temp={field4}")
                    c.execute("INSERT INTO sensor_data (GAS,  SMOKE, TEMP_sys, Temp, DATE, TIME) VALUES (?,?,?,?,?,?)", (field1, field2, field3, field4, date, time))
                    conn.commit()
                    # Gửi dữ liệu lên Blynk
                    blynk.virtual_write(0, field1) #Gas
                    blynk.virtual_write(2, field2) #Smoke
                    blynk.virtual_write(3, field3) #Temp_sys
                    blynk.virtual_write(1, field4) #Temp
                    print("Values sent to New Blynk Server! 1111")
                    sleep(1)
                except ValueError:
                    print("Error parsing received data.")
            ser.write(str('2').encode())  # Gửi tín hiệu 'READY' tới STM32 để báo rằng Pi đã sẵn sàng
            ser.flush()
            if ser.in_waiting > 0:
                try:
                    received_data1 = ser.readline().decode().strip()
                    field5, field6 , field7, field8 = map(int, received_data1.split(','))
                    print("Node 2:")
                    print(f"Gas={field5},Smoke ={field6} ,Temp_sys={field7}, Temp={field8}")
                    #c.execute("INSERT INTO sensor_data (GAS,  SMOKE, TEMP_sys, Temp, DATE, TIME) VALUES (?,?,?,?,?,?)", (field1, field2, field3, field4, date, time))
                    #conn.commit()
                    # Gửi dữ liệu lên Blynk
                    blynk.virtual_write(8, field5) #Gas
                    blynk.virtual_write(6, field6) #Smoke
                    blynk.virtual_write(7, field7) #Temp_sys
                    blynk.virtual_write(5, field8) #Temp
                    print("Values sent to New Blynk Server! 2222")
                    sleep(1)
                    break
                except ValueError:
                    print("Error parsing received data.")

    except serial.SerialException as e:
        print(f"Serial exception: {e}")

# Thiết lập timer để gọi hàm receive_data
timer.set_interval(3, receive_data)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Chân nút nhấn
GPIO.setup(LED_GPIO, GPIO.OUT)                               # Chân LED
GPIO.output(LED_GPIO, GPIO.LOW)                              # Mặc định tắt LED

# Thiết lập ngắt GPIO với thời gian chống dội
GPIO.add_event_detect(BUTTON_GPIO, GPIO.RISING, 
                        callback=button_callback, bouncetime=200)

# Bắt tín hiệu Ctrl+C để dọn dẹp GPIO
signal.signal(signal.SIGINT, signal_handler)
try:
    while True:
        blynk.run()
        timer.run()
finally:
    conn.close()  # Đảm bảo kết nối được đóng khi chương trình kết thúc
