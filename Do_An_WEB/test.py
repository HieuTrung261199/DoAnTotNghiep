import numpy as np
from tensorflow.keras.models import load_model

model = load_model('model_du_bao_chay.h5')

time_steps = 10
num_features = 3

random_data = np.random.uniform(low=0, high=100, size=(time_steps, num_features))

print("Dữ liệu ngẫu nhiên:")
print(random_data)

random_data = np.expand_dims(random_data, axis=0)
prediction = model.predict(random_data)
result = "Cháy" if prediction > 0.5 else "Không cháy"
print(f"Kết quả dự đoán: {result}")
