import numpy as np
from tensorflow.keras.models import load_model
import sqlite3

class PredictModel:
    def __init__(self):
        self.model = load_model('model_du_bao_chay.h5')
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect('iot_data.db')
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def lstm_model(self):
        self.connect()
        self.cursor.execute("""
            SELECT GAS, TEMP, SMOKE FROM sensor_data
            ORDER BY DATE DESC, TIME DESC LIMIT 10
        """)
        data = self.cursor.fetchall() 
        data = np.array(data).reshape(1, 10, 3)
        prediction = self.model.predict(data)
        result = "Cháy" if prediction > 0.5 else "Không cháy"
        return result
    
if __name__ == "__main__":
    p = PredictModel()
    l =p.lstm_model()