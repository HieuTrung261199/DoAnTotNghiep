from flask import Flask, render_template, request, jsonify, redirect, flash, url_for, session
from database.login import Login
from flask_cors import CORS
import sqlite3
import requests
from AI import LSTM

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

raspberry_pi_url = "http://192.168.1.10:5006/receive_push"  

# Trang chính
@app.route("/")
def home():
    return redirect(url_for("login"))

# Đăng nhập
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        path = 'database/data.db'
        login_db = Login(path)
        select = login_db.select_information(username, password)
        if select:
            session['user'] = username
            flash('Đăng nhập thành công', 'success')
            return redirect(url_for("select"))
        else:
            flash('Sai tài khoản hoặc mật khẩu', 'error')
            return redirect(url_for("login"))
    return render_template('login.html')

# Trang lựa chọn
@app.route("/select")
def select():
    if 'user' not in session:
        flash('Vui lòng đăng nhập', 'error')
        return redirect(url_for("login"))
    return render_template('select.html')

# Đăng ký
@app.route("/register", methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    path = 'database/data.db'
    login_db = Login(path)
    insert_db = login_db.insert_information(username, password, email)
    if insert_db:
        flash('Đăng ký thành công', 'success')
    else:
        flash('Tài khoản đã tồn tại', 'error')
        return redirect(url_for("login"))
    return redirect(url_for("login"))

# Nhận dữ liệu từ Raspberry Pi
@app.route('/upload_data', methods=['POST'])
def upload_data():
    """Nhận dữ liệu từ Raspberry Pi và lưu vào cơ sở dữ liệu"""
    data = request.json  # Nhận dữ liệu từ Raspberry Pi
    if data and all(key in data for key in ["gas", "temp", "smoke", "temp_sys","date","time", "node_id"]):
        # Kiểm tra và đảm bảo rằng dữ liệu có tất cả các trường cần thiết
        node_id = data["node_id"]  # Lấy NODE_ID từ dữ liệu
        print(f"Received data for Node {node_id}: {data}")

        # Lưu dữ liệu vào cơ sở dữ liệu
        conn = sqlite3.connect('iot_data.db')
        cursor = conn.cursor()
        query = """
            INSERT INTO sensor_data (GAS, TEMP, SMOKE, TEMP_SYS,DATE,TIME,NODE_ID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (data['gas'], data['temp'], data['smoke'], data['temp_sys'],data['date'],data['time'] ,data['node_id']))
        conn.commit()
        conn.close()

        # Trả về phản hồi với status thành công
        response_data = {
            "node_id": node_id,
            "received_data": {
                "gas": data['gas'],
                "temp": data['temp'],
                "smoke": data['smoke'],
                "temp_sys": data['temp_sys'],
                "date": data['date'],
                "time" :data['time'],
                "node_id": data['node_id']
            }
        }
        return jsonify({"status": "success", "data": response_data}), 200
    else:
        return jsonify({"status": "failed", "message": "Dữ liệu không hợp lệ hoặc thiếu trường bắt buộc"}), 400


# Hàm chung lấy dữ liệu từ cơ sở dữ liệu
def get_node_data(node_id):
    conn = sqlite3.connect('iot_data.db')
    cursor = conn.cursor()
    query = """
        SELECT GAS, TEMP, SMOKE, TEMP_SYS ,TIME
        FROM sensor_data 
        WHERE NODE_ID = ? 
        ORDER BY DATE DESC, TIME DESC 
        LIMIT 30
    """
    cursor.execute(query, (node_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# API dữ liệu cho từng node
@app.route('/Data/node<int:node_id>', methods=['GET'])
def get_node_data_api(node_id):
    data = get_node_data(node_id)
    if not data:
        return jsonify({"error": f"Node {node_id} không tồn tại hoặc không có dữ liệu"}), 404
    
    # Chuyển dữ liệu thành dạng phù hợp cho biểu đồ
    formatted_data = [{"gas": row[0], "temp": row[1], "smoke": row[2], "temp_sys": row[3],"Time": row[4]} for row in data]
    
    return jsonify(formatted_data)

# Trang hiển thị biểu đồ
@app.route("/ai")
def ai():
    return render_template('index.html')

@app.route("/chart")
def search():
    if 'user' not in session:
        flash('Vui lòng đăng nhập', 'error')
        return redirect(url_for("login"))
    return render_template('chart.html')

# Trang giao diện AI
@app.route('/api/data', methods=['GET'])
def get_data():
    # Dữ liệu trả về dưới dạng JSON
    lstm = LSTM.PredictModel()
    result = lstm.lstm_model()
    data = {
        'message': 'Dữ liệu từ API',
        'prediction': result
    }
    return jsonify(data)

# Trang giao diện kích hoạt báo cháy
@app.route('/Push', methods=['GET', 'POST'])
def push():
    if 'user' not in session:
        flash('Vui lòng đăng nhập', 'error')
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        try:
            # Địa chỉ IP của Raspberry Pi và endpoint 
            # Gửi dữ liệu POST với số 1
            response = requests.post(raspberry_pi_url, json={"push_signal": 1})
            if response.status_code == 200:
                flash('Dữ liệu đã gửi thành công đến Raspberry Pi!', 'success')
            else:
                flash(f'Lỗi khi gửi dữ liệu đến Raspberry Pi: {response.text}', 'error')
        except requests.exceptions.RequestException as e:
            flash(f'Không thể kết nối với Raspberry Pi: {str(e)}', 'error')
    
    return render_template('Push.html')

# Trang giao diện kích hoạt báo cháy
@app.route('/OFF', methods=['GET', 'POST'])
def Off():
    if 'user' not in session:
        flash('Vui lòng đăng nhập', 'error')
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        try:
            # Gửi dữ liệu POST với số 1
            response = requests.post(raspberry_pi_url, json={"push_signal": 0})
            if response.status_code == 200:
                flash('Dữ liệu đã gửi thành công đến Raspberry Pi!', 'success')
            else:
                flash(f'Lỗi khi gửi dữ liệu đến Raspberry Pi: {response.text}', 'error')
        except requests.exceptions.RequestException as e:
            flash(f'Không thể kết nối với Raspberry Pi: {str(e)}', 'error')
    
    return render_template('Push.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
