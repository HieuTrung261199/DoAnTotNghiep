import BlynkLib
from BlynkTimer import BlynkTimer
import serial
from datetime import datetime
import sqlite3
from time import sleep
import signal
import sys
import RPi.GPIO as GPIO

# Kết nối SQLite
conn = sqlite3.connect('iot_data.db')
c = conn.cursor()

# Tạo bảng nếu chưa tồn tại
c.execute('''
CREATE TABLE IF NOT EXISTS sensor_data (
    GAS INT,
    TEMP INT,
    SMOKE INT,
    TEMP_sys INT,
    NODE_ID INT,
    DATE TEXT,
    TIME TEXT
)
''')

# Cấu hình GPIO
BUTTON_GPIO = 16
LED_GPIO = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_GPIO, GPIO.OUT)
GPIO.output(LED_GPIO, GPIO.LOW)

# Cấu hình Blynk
BLYNK_AUTH_TOKEN = 'xnWepqN6sHxDLgZJLSOpvuTU9KMmMe1C'
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)
timer = BlynkTimer()

# Cấu hình UART
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Biến toàn cục
led_state = True

# Xử lý tín hiệu Ctrl+C
def signal_handler(sig, frame):
    GPIO.cleanup()
    conn.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Hàm xử lý nút nhấn
def button_callback(channel):
    global led_state
    led_state = not led_state
    ser.write(b'8' if led_state else b'9')
    ser.flush()
    print("LED ON" if led_state else "LED OFF")

GPIO.add_event_detect(BUTTON_GPIO, GPIO.RISING, callback=button_callback, bouncetime=200)

# Hàm đồng bộ dữ liệu khi kết nối Blynk
@blynk.on("connected")
def blynk_connected():
    print("Connected to Blynk server!")

# Điều khiển LED qua Blynk
@blynk.on("V4")
def v4_write_handler(value):
    ser.write(b'8' if int(value[0]) else b'9')
    ser.flush()
    print("LED ON" if int(value[0]) else "LED OFF")

# Hàm đọc dữ liệu từ từng node
def read_node_data(node_id):
    ser.write(str(node_id).encode())
    ser.flush()
    sleep(1)  # Đảm bảo STM32 có thời gian gửi dữ liệu
    if ser.in_waiting > 0:
        try:
            raw_data = ser.readline().decode().strip()
            print(f"Raw Node {node_id} Data: {raw_data}")
            fields = list(map(int, raw_data.split(',')))
            return fields  # Trả về danh sách dữ liệu
        except ValueError:
            print(f"Error parsing Node {node_id} data.")
    else:
        print(f"No data received from Node {node_id}.")
    return None

# Hàm xử lý và lưu dữ liệu
def process_and_store_data(node_id, data):
    if data:
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")
        gas, smoke, temp_sys, temp = data
        print(f"Node {node_id} Data: Gas={gas}, Smoke={smoke}, Temp_sys={temp_sys}, Temp={temp}")
        
        # Lưu vào cơ sở dữ liệu
        c.execute("INSERT INTO sensor_data (GAS, SMOKE, TEMP_sys, TEMP, NODE_ID, DATE, TIME) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (gas, smoke, temp_sys, temp, node_id, date, time))
        conn.commit()
        
        # Gửi dữ liệu lên Blynk
        if node_id == 1:
            blynk.virtual_write(0, gas)       # Gas
            blynk.virtual_write(2, smoke)    # Smoke
            blynk.virtual_write(3, temp_sys) # Temp_sys
            blynk.virtual_write(1, temp)     # Temp
        elif node_id == 2:
            blynk.virtual_write(8, gas)      # Gas
            blynk.virtual_write(6, smoke)    # Smoke
            blynk.virtual_write(7, temp_sys) # Temp_sys
            blynk.virtual_write(5, temp)     # Temp

# Hàm chính để nhận dữ liệu từ cả hai node
def receive_data():
    print("Receiving data from nodes...")
    # Đọc dữ liệu từ Node 1
    node_1_data = read_node_data(1)
    process_and_store_data(1, node_1_data)
    
    # Đọc dữ liệu từ Node 2
    node_2_data = read_node_data(2)
    process_and_store_data(2, node_2_data)

# Thiết lập timer để gọi hàm nhận dữ liệu
timer.set_interval(3, receive_data)

# Chạy chương trình chính
try:
    while True:
        blynk.run()
        timer.run()
finally:
    conn.close()
    GPIO.cleanup()
