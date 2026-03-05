import os
import numpy as np
import joblib
import tensorflow as tf
from django.conf import settings

# ==============================
# PATHS
# ==============================
BASE_DIR = settings.BASE_DIR

CROP_MODEL_PATH = os.path.join(BASE_DIR, 'ml/models/crop_recommendation_model.h5')
YIELD_MODEL_PATH = os.path.join(BASE_DIR, 'ml/models/yield_prediction_model.h5')

CROP_SCALER_PATH = os.path.join(BASE_DIR, 'ml/models/crop_scaler.pkl')
YIELD_SCALER_PATH = os.path.join(BASE_DIR, 'ml/models/yield_scaler.pkl')

LABEL_ENCODER_PATH = os.path.join(BASE_DIR, 'ml/models/crop_label_encoder.pkl')

# ==============================
# LOAD MODELS ONCE
# ==============================

crop_model = tf.keras.models.load_model(CROP_MODEL_PATH, compile=False)
yield_model = tf.keras.models.load_model(YIELD_MODEL_PATH, compile=False)


crop_scaler = joblib.load(CROP_SCALER_PATH)
yield_scaler = joblib.load(YIELD_SCALER_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)


# ==============================
# CROP PREDICTION
# ==============================

def predict_crop(n, p, k, temp, hum, ph, rain):
    input_data = np.array([[n, p, k, temp, hum, ph, rain]])
    input_scaled = crop_scaler.transform(input_data)

    prediction = crop_model.predict(input_scaled)
    predicted_index = np.argmax(prediction)

    predicted_crop = label_encoder.inverse_transform([predicted_index])[0]
    confidence = float(np.max(prediction)) * 100

    return predicted_crop, round(confidence, 2)


# ==============================
# YIELD PREDICTION
# ==============================
def predict_yield(area, season, crop_name):

    # Create empty feature vector with all 131 features
    feature_names = yield_scaler.feature_names_in_
    input_dict = {feature: 0 for feature in feature_names}

    # Set Area
    if 'Area' in input_dict:
        input_dict['Area'] = area

    # Clean season and crop values (strip spaces)
    season = season.strip()
    crop_name = crop_name.strip()

    # Match exact feature names (very important)
    for feature in feature_names:
        if feature.strip() == f"Season_{season}":
            input_dict[feature] = 1

        if feature.strip() == f"Crop_{crop_name}":
            input_dict[feature] = 1

    # Convert to correct order array
    input_vector = np.array([[input_dict[feature] for feature in feature_names]])

    # Scale
    input_scaled = yield_scaler.transform(input_vector)

    # Predict
    prediction = yield_model.predict(input_scaled)

    return round(float(prediction[0][0]), 2)
