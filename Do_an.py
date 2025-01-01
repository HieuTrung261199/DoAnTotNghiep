from flask import Flask, request, jsonify
import sqlite3
import requests
import serial
from datetime import datetime
from time import sleep
import signal
import sys
import RPi.GPIO as GPIO
import threading
import json
import pymongo


# Telegram Bot Token và Chat ID
BOT_TOKEN = '7417109892:AAFxciSodWmXPLJYE2ZeMMPUIn2OUn5FaBU'
CHAT_ID = '7547581341'  # Thay bằng Chat ID của bạn

myclient = pymongo.MongoClient("mongodb+srv://Pi:1@dataforsensor.bidtxu2.mongodb.net/?retryWrites=true&w=majority&appName=DataForSensor")
mydb = myclient["mydatabase"]
mycol = mydb["SensorData"]

# URL API Telegram
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

# Hàm gửi tin nhắn tới bot
def send_message(message):
    try:
        payload = {
            'chat_id': CHAT_ID,
            'text': message
        }
        response = requests.post(TELEGRAM_API_URL, json=payload)
        if response.status_code == 200:
            print(f"Đã gửi tin nhắn: {message}")
        else:
            print(f"Lỗi khi gửi tin nhắn: {response.status_code}")
    except Exception as e:
        print(f"Lỗi khi kết nối API: {e}")



def start_flask():
    app.run(host='0.0.0.0', port=5006, debug=True)


# Cấu hình cơ bản
app = Flask(__name__)

FLASK_URL = 'http://192.168.1.10:5000/upload_data'  # URL máy tính

# Đường dẫn tới cơ sở dữ liệu trên Raspberry Pi
DB_PATH = 'iot_data.db'

# Kết nối cơ sở dữ liệu
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

# Tạo bảng nếu chưa tồn tại
c.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
    GAS INT,
    TEMP INT,
    SMOKE INT,
    TEMP_sys INT,
    NODE_ID INT,
    DATE TEXT,
    TIME TEXT
)''')
conn.commit()

# Cấu hình GPIO
BUTTON_GPIO = 16
LED_GPIO = 19
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_GPIO, GPIO.OUT)
GPIO.output(LED_GPIO, GPIO.LOW)

# Biến toàn cục
led_state = False
check1 = True

# Khởi tạo serial cho việc giao tiếp UART
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Xử lý tín hiệu Ctrl+C
def signal_handler(sig, frame):
    GPIO.cleanup()
    conn.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Hàm đếm giờ
def countdown(seconds):
    while seconds > 0:
        print(f"countdown: {seconds} seconds")
        sleep(1)
        seconds -= 1

# Xử lý nút nhấn
def button_callback(channel):
    global check1, led_state
    check1 = False
    '''ser.write(str('5').encode())
    ser.flush()'''
    print("Ready!!!!!!!!!")
    countdown(10)
    led_state = not led_state  # Đảo trạng thái LED
    if led_state:
        ser.write(str('8').encode())
        ser.flush()
        GPIO.output(LED_GPIO, GPIO.HIGH)
        print("ON")
        send_message("Báo cháy được kích hoạt bằng nút nhấn")
    else:
        ser.write(str('9').encode())
        ser.flush()
        GPIO.output(LED_GPIO, GPIO.LOW)
        print("OFF")
        send_message("Báo cháy được tắt bằng nút nhấn")
    check1 = True
    print(check1)

GPIO.add_event_detect(BUTTON_GPIO, GPIO.RISING, callback=button_callback, bouncetime=200)

# Đọc dữ liệu từ một node qua UART
def read_node_data(node_id):
    ser.write(str(node_id).encode())
    ser.flush()
    sleep(1)
    raw_data = None 
    if ser.in_waiting > 0:
        try:
            raw_data = ser.readline().decode().strip()
            raw1 = raw_data[0]
            if raw1 == 'Q' or raw1 == 'W' or raw1 == 'E':
                if raw1 == 'Q':
                    send_message("Phòng của Node 1 đang xảy ra cháy!!!!")
                elif raw1 == 'W':
                    send_message("Phòng của Node 2 đang xảy ra cháy!!!!")
                elif raw1 == 'E':
                    send_message("Phòng của Node 3 đang xảy ra cháy!!!!")
                print(f"Raw Node {node_id} Data: {raw_data}")
                raw_data = raw_data[1:]  # Bỏ ký tự đầu tiên nếu có
                fields = list(map(int, raw_data.split(',')))
                if len(fields) == 4:  # Chỉ chấp nhận dữ liệu có đúng 4 trường
                    return fields
                else:
                    print(f"Node {node_id}: Invalid data length ({len(fields)} fields). Expected 4.")
                    return None
            else:
                print(f"Raw Node {node_id} Data: {raw_data}")
                raw_data = raw_data[1:]  # Bỏ ký tự đầu tiên nếu có
                fields = list(map(int, raw_data.split(',')))
                if len(fields) == 4:  # Chỉ chấp nhận dữ liệu có đúng 4 trường
                    return fields
                else:
                    print(f"Node {node_id}: Invalid data length ({len(fields)} fields). Expected 4.")
                    return None
        except ValueError:
            print(f"Node {node_id}: Error parsing data. Received raw data: {raw_data}")
    print(f"Node {node_id}: No data received.")
    return None


def start_flask():
    app.run(host='0.0.0.0', port=5006, debug=True, use_reloader=False)

# Hàm nhận dữ liệu
def receive_data_loop():
    while True:
        global check1
        if check1 == True:
            receive_data()  # Gọi hàm nhận dữ liệu từ các node
            sleep(5)  # Đảm bảo không bị tắc nghẽn

# Xử lý và gửi dữ liệu từ node
def process_and_send_data(node_id, data):
    if data:
        try:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")
            gas, smoke, temp_sys, temp = data
            c.execute("INSERT INTO sensor_data (GAS, SMOKE, TEMP_sys, TEMP, NODE_ID, DATE, TIME) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (gas, smoke, temp_sys, temp, node_id, date, time))
            conn.commit()
            print(f"Node {node_id} Data: Gas={gas}, Smoke={smoke}, Temp_sys={temp_sys}, Temp={temp}")

            # Gửi dữ liệu đến Flask server
            mydict = {
                "gas": gas,
                "smoke": smoke,
                "temp_sys": temp_sys,
                "temp": temp,
                "date": date,
                "time" :time,
                "node ID": node_id
                }
            response = requests.post(FLASK_URL, json={
                "gas": gas,
                "smoke": smoke,
                "temp_sys": temp_sys,
                "temp": temp,
                "date": date,
                "time" :time,
                "node_id": node_id
            })
            mycol.insert_one(mydict)
            if response.status_code == 200:
                print(f"Data from Node {node_id} sent successfully!")
            else:
                print(f"Failed to send data from Node {node_id}. Error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data from Node {node_id}: {e}")

# Nhận và xử lý dữ liệu từ các node
def receive_data():
    node_ids = [1, 2, 3]  # Các node cần nhận dữ liệu
    for node_id in node_ids:
        node_data = read_node_data(node_id)
        if node_data:
            process_and_send_data(node_id, node_data)
        sleep(5)
        print("---------------------")

# API để nhận tín hiệu từ phía ngoài
@app.route('/receive_push', methods=['POST'])
def receive_push():
    global check1
    data = request.json
    print("Ready!!!!!!!!!")
    print("Received data:", data)
    if data and data.get('push_signal') == 1:
        check1 = False
        '''ser.write(str('5').encode())
        ser.flush()'''
        countdown(5)
        GPIO.output(LED_GPIO, GPIO.HIGH)
        ser.write(b'8')
        ser.flush()
        print("LED ON")
        send_message("Báo cháy được kích hoạt bằng Web")
        check1 = True
        return jsonify({"status": "success", "message": "Dữ liệu đã được gửi."}), 200
    elif data and data.get('push_signal') == 0:
        check1 = False
        '''ser.write(str('5').encode())
        ser.flush()'''
        countdown(5)
        GPIO.output(LED_GPIO, GPIO.LOW)
        ser.write(b'9')
        ser.flush()
        print("LED OFF")
        send_message("Báo cháy tắt kích hoạt bằng Web")
        check1 = True
        return jsonify({"status": "success", "message": "Tắt LED thành công."}), 200
    return jsonify({"status": "failed", "message": "Tín hiệu không hợp lệ."}), 400

# Main loop để nhận dữ liệu liên tục
if __name__ == '__main__':
    # Tạo và bắt đầu thread cho Flask
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True  # Đảm bảo thread này sẽ kết thúc khi chương trình chính kết thúc
    flask_thread.start()

    # Tạo và bắt đầu thread cho hàm nhận dữ liệu
    receive_data_thread = threading.Thread(target=receive_data_loop)
    receive_data_thread.daemon = True
    receive_data_thread.start()

    # Giữ cho chương trình chạy liên tục
    while True:
        sleep(1)  # Để chương trình chính không kết thúc quá sớm
