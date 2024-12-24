from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Hàm lấy dữ liệu từ cơ sở dữ liệu cho mỗi node
def get_node_data(node_id):
    conn = sqlite3.connect('iot_data.db')
    cursor = conn.cursor()
    
    # Truy vấn dữ liệu cho node_id cụ thể
    query = "SELECT GAS, TEMP, SMOKE, TEMP_SYS FROM sensor_data WHERE node_id = ?"
    cursor.execute(query, (node_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return rows

# API cho Node 1
@app.route('/Data/node1')
def get_node1_data():
    data = get_node_data(1)  # Lấy dữ liệu của Node 1
    return jsonify(data)

# API cho Node 2
@app.route('/Data/node2')
def get_node2_data():
    data = get_node_data(2)  # Lấy dữ liệu của Node 2
    return jsonify(data)

# API cho Node 3
@app.route('/Data/node3')
def get_node3_data():
    data = get_node_data(3)  # Lấy dữ liệu của Node 3
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
