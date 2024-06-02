import paho.mqtt.client as mqtt
from datetime import datetime
from time import sleep
from urllib import request
import serial
import json
from urllib import request, parse

def make_param_thingspeak(temp, smoke, IR, Mq):
    params = parse.urlencode({'field1': temp, 'field3': somke,'field2': IR, 'field4': Mq }).encode()
    return params
def thingspeak_post(params):
    api_key_write = "4OG7A73RK06C9ZJD"
    req = request.Request('https://api.thingspeak.com/update',method="POST")
    req.add_header("Content-Type","application/x-www-form-urlencoded")
    req.add_header("X-THINGSPEAKAPIKEY",api_key_write)
    r = request.urlopen(req, data = params)
    respone_data = r.read()
    return respone_data
def receive_data():
    # Cấu hình cổng serial
    ser = serial.Serial(
        port='/dev/serial0',  # Cổng UART mặc định trên Raspberry Pi
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )

    # Kiểm tra xem cổng serial đã mở chưa
    if ser.isOpen():
        print("Cổng serial đã mở.")
    else:
        print("Mở cổng serial thất bại.")
        return

    print("Đang chờ nhận dữ liệu từ Hercules...")
        # Đọc dữ liệu
    if ser.in_waiting > 0:
      received_data = ser.readline().decode('utf-8').strip()
      field1, field3,field2, field4 = map(int, received_data.split(','))
      print(f"Field1={field1}, Field3={field3},Field2={field2}, Field4={field4}")
      params_thingspeak = make_param_thingspeak(field1,field3,field2,field4)
      thingspeak_post(params_thingspeak)
      print("Done!!!!!")
            
                
def thingspeak_get_data():
    api_key_read = "OXSMDWPRN00P5A30"
    # Lấy dữ liệu từ field_num
    req = request.Request("https://api.thingspeak.com/channels/2562559/feeds.json?api_key=4OG7A73RK06C9ZJD", method="GET")
    r = request.urlopen(req)
    response_data = r.read().decode()
    response_data = json.loads(response_data)
    # Dữ liệu lịch sử là một danh sách các mục
    data = response_data["feeds"]
    data_c = response_data["channel"]
    return data ,data_c
if __name__ == "__main__":
    while True:
        data,data_c = thingspeak_get_data()
        try:
            a_m =data[len(data)-1]['field%s'%(5)]
            a_m = int(a_m)
        except:
            a_m = a_m
        if a_m == 1:
            ser = serial.Serial(
                port = '/dev/serial0',
                baudrate = 115200,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS,
                timeout = 1000
            )
            ser.write(str('1').encode())
            ser.flush()
            print("ON")
            sleep(1)
        if a_m == 0:
            ser = serial.Serial(
                port = '/dev/serial0',
                baudrate = 115200,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS,
                timeout = 1000
            )
            ser.write(str('0').encode())
            ser.flush()
            print("OFF")
            sleep(1)
        receive_data()
        sleep(3)
 
 
 
        
import serial
import time

def receive_data():
    # Cấu hình cổng serial
    ser = serial.Serial(
        port='/dev/serial0',  # Cổng UART mặc định trên Raspberry Pi
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
    ser.flush()

    # Kiểm tra xem cổng serial đã mở chưa
    if ser.isOpen():
        print("Cổng serial đã mở.")
    else:
        print("Mở cổng serial thất bại.")
        return

    while True:
        # Đọc dữ liệu
        if ser.in_waiting > 0:
            received_data = ser.readline().decode().strip()
            try:
                field1, field3, field2, field4 = map(int, received_data.split(','))
                print(f"Field1={field1}, Field3={field3}, Field2={field2}, Field4={field4}")
            except ValueError:
                print("Dữ liệu nhận được không hợp lệ")
            
            time.sleep(2)

if __name__ == "__main__":
    receive_data()

    
    
    