import paho.mqtt.client as mqtt
from datetime import datetime
from time import sleep
from urllib import request, parse
import serial
import json
import pymongo

# Kết nối tới MongoDB
myclient = pymongo.MongoClient("mongodb+srv://Pi:1@dataforsensor.bidtxu2.mongodb.net/?retryWrites=true&w=majority&appName=DataForSensor")
mydb = myclient["mydatabase"]
mycol = mydb["SensorData"]

# Hàm tạo tham số cho ThingSpeak
def make_param_thingspeak(temp, IR, mq2, mq1):
    params = parse.urlencode({'field1': temp, 'field2': IR, 'field3': mq2, 'field4': mq1}).encode()
    return params

# Hàm gửi dữ liệu tới ThingSpeak
def thingspeak_post(params):
    api_key_write = "4OG7A73RK06C9ZJD"
    req = request.Request('https://api.thingspeak.com/update', method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("X-THINGSPEAKAPIKEY", api_key_write)
    r = request.urlopen(req, data=params)
    response_data = r.read()
    return response_data

# Hàm nhận dữ liệu từ cổng serial
def receive_data():
    ser = serial.Serial(
        port='/dev/serial0',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )

    if ser.isOpen():
        print("Cổng serial đã mở.")
    else:
        print("Mở cổng serial thất bại.")
        return

    print("Đang chờ nhận dữ liệu từ ...")
    while True:
        ser.write(str('11').encode())  # Gửi tín hiệu 'READY' tới STM32 để báo rằng Pi đã sẵn sàng
        ser.flush()
        if ser.in_waiting > 0:
            try:
                received_data = ser.readline().decode().strip()
                field1, field2, field3, field4 = map(int, received_data.split(','))
                print(f"Field1={field1}, Field2={field2}, Field3={field3}, Field4={field4}")

                params_thingspeak = make_param_thingspeak(field1, field2, field3, field4)
                thingspeak_post(params_thingspeak)

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                mydict = {
                    "Temp": field1,
                    "IR": field2,
                    "Mq-2": field3,
                    "Mq-135": field4,
                    "timestamp": current_time
                }
                mycol.insert_one(mydict)
                print("Hoàn thành!!!!!")
                sleep(3)  # Chờ 3 giây để khớp với tần suất gửi dữ liệu của STM32
            except Exception as e:
                print(f"Đã xảy ra lỗi khi nhận dữ liệu: {e}")

# Hàm lấy dữ liệu từ ThingSpeak
def thingspeak_get_data():
    api_key_read = "OXSMDWPRN00P5A30"
    req = request.Request("https://api.thingspeak.com/channels/2562559/feeds.json?api_key=4OG7A73RK06C9ZJD", method="GET")
    r = request.urlopen(req)
    response_data = r.read().decode()
    response_data = json.loads(response_data)
    data = response_data["feeds"]
    data_c = response_data["channel"]
    return data, data_c

if __name__ == "__main__":
    while True:
        try:
            data, data_c = thingspeak_get_data()
            try:
                a_m = data[len(data) - 1]['field%s' % (5)]
                a_m = int(a_m)
            except:
                a_m = None
            if a_m == 1:
                ser = serial.Serial(
                    port='/dev/serial0',
                    baudrate=115200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1000
                )
                ser.write(str('1').encode())
                ser.flush()
                print("BẬT")
            elif a_m == 0:
                ser = serial.Serial(
                    port='/dev/serial0',
                    baudrate=115200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1000
                )
                ser.write(str('0').encode())
                ser.flush()
                print("TẮT")
            receive_data()
            sleep(3)  # Chờ 3 giây trước khi bắt đầu vòng lặp tiếp theo
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
            sleep(5)
