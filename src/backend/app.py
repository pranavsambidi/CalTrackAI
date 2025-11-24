import os
import time
import uuid
import json
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, Response
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from rapidfuzz import process, fuzz
from datetime import datetime

# ---------------------------
# PROMETHEUS
# ---------------------------
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# =====================================================
# CONFIG
# =====================================================
MODEL_PATH = "./model/resnet50_food101_final.keras"
LABEL_MAP_PATH = "./data/label_map.json"
USDA_PATH = "./data/usda_food_data.csv"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

FEEDBACK_FILE = "./data/feedback.jsonl"  # JSON Lines file
os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)

# =====================================================
# PROMETHEUS METRICS
# =====================================================
PREDICTION_REQUESTS = Counter(
    "prediction_requests_total",
    "Total number of prediction requests"
)

PREDICTION_ERRORS = Counter(
    "prediction_errors_total",
    "Total number of failed prediction requests"
)

PREDICTION_LATENCY = Histogram(
    "prediction_latency_seconds",
    "Time taken to run prediction"
)

PREDICTION_CONFIDENCE = Histogram(
    "prediction_confidence",
    "Top-1 confidence of predictions",
    buckets=[0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
)

FEEDBACK_YES = Counter(
    "feedback_yes_total",
    "Total number of positive feedback responses"
)

FEEDBACK_NO = Counter(
    "feedback_no_total",
    "Total number of negative feedback responses"
)


# =====================================================
# LOAD MODEL + LABEL MAP
# =====================================================
print("Loading model...")
model = load_model(MODEL_PATH)

print("Loading label map...")
with open(LABEL_MAP_PATH, "r") as f:
    label_map = json.load(f)

idx_to_label = {v: k for k, v in label_map.items()}

print("Loading USDA CSV...")
usda_df = pd.read_csv(USDA_PATH)

# lower-case description for fuzzy search
usda_df["desc_lower"] = usda_df["description"].astype(str).str.lower()


# =====================================================
# NUTRITION FUZZY MATCH FUNCTION
# =====================================================
def find_nutrition(food_label):
    """
    Fuzzy-match model label → USDA entry.
    Guaranteed match as long as similarity >= 60.
    """
    clean = food_label.replace("_", " ").lower()

    match = process.extractOne(
        clean,
        usda_df["desc_lower"],
        scorer=fuzz.WRatio
    )

    if not match:
        return None

    score, index = match[1], match[2]

    if score < 60:   # similarity threshold
        return None

    row = usda_df.iloc[index]

    return {
        "description": row["description"],
        "calories": float(row["calories"]) if not pd.isna(row["calories"]) else None,
        "protein": float(row["protein"]) if not pd.isna(row["protein"]) else None,
        "fat": float(row["fat"]) if not pd.isna(row["fat"]) else None,
        "carbohydrates": float(row["carbohydrates"]) if not pd.isna(row["carbohydrates"]) else None
    }


# =====================================================
# FOOD PREDICTION
# =====================================================
def predict_food(img_path):
    """Runs model inference + fuzzy USDA match."""
    img = image.load_img(img_path, target_size=(224, 224))
    img_arr = image.img_to_array(img)
    img_arr = preprocess_input(img_arr)
    img_arr = np.expand_dims(img_arr, axis=0)

    preds = model.predict(img_arr)
    top5_idx = preds[0].argsort()[-5:][::-1]

    predictions = []
    for idx in top5_idx:
        predictions.append({
            "label": idx_to_label[idx],
            "confidence": float(preds[0][idx])
        })

    # Prometheus metric
    PREDICTION_CONFIDENCE.observe(predictions[0]["confidence"])

    # Nutrition lookup for top-1
    nutrition = find_nutrition(predictions[0]["label"])

    return predictions, nutrition


# =====================================================
# FLASK APP
# =====================================================
app = Flask(__name__)


# -------------------------
# PROMETHEUS METRICS ROUTE
# -------------------------
@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# -------------------------
# HOME
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return "CalTrackAI API is running with Prometheus metrics!"


# -------------------------
# PREDICT ENDPOINT
# -------------------------
@app.route("/predict", methods=["POST"])
def predict():
    PREDICTION_REQUESTS.inc()
    start_time = time.time()

    try:
        if "image" not in request.files:
            PREDICTION_ERRORS.inc()
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]

        # Save image temporarily
        ext = file.filename.rsplit(".", 1)[-1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)

        # Predict
        predictions, nutrition = predict_food(filepath)

        # Clean file
        os.remove(filepath)

        # Return JSON
        return jsonify({
            "top1": predictions[0],
            "top5": predictions,
            "nutrition": nutrition
        })

    except Exception as e:
        PREDICTION_ERRORS.inc()
        return jsonify({"error": str(e)}), 500

    finally:
        PREDICTION_LATENCY.observe(time.time() - start_time)


@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json

    if data.get("feedback_type") == "yes":
        FEEDBACK_YES.inc()
    else:
        FEEDBACK_NO.inc()

    with open(FEEDBACK_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

    return jsonify({"status": "success"})


# =====================================================
# RUN SERVER
# =====================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
