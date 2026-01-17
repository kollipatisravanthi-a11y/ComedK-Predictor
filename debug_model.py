import joblib
import os

model_path = r'c:\Projects\COMEDK_DTL\backend\chatbot_model.pkl'
if os.path.exists(model_path):
    model = joblib.load(model_path)
    msg = "courses"
    probs = model.predict_proba([msg])[0]
    import numpy as np
    pred = model.classes_[np.argmax(probs)]
    print(f"Prediction for '{msg}': {pred}")
    print(f"Probabilities: {dict(zip(model.classes_, probs))}")
else:
    print("Model not found")
