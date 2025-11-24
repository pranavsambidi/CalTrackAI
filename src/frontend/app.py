import streamlit as st
import requests
import json
import pandas as pd
from PIL import Image
import io
import matplotlib.pyplot as plt
import plotly.express as px 

# --------------------------
# CONFIG
# --------------------------
API_URL = "http://backend:3000/predict"

st.set_page_config(page_title="CalTrackAI – Food Recognition", layout="centered")

st.title("CalTrackAI – Automated Nutrition Tracking from Photos")
st.write(
    """
Upload a food image → The model predicts the dish and estimates its nutritional values.

> **Note:** Nutrition values returned are based on a **100g serving** of the predicted food.
"""
)

# --------------------------------------
# SESSION STATE (to persist results & feedback)
# --------------------------------------
if "api_result" not in st.session_state:
    st.session_state.api_result = None

if "feedback" not in st.session_state:
    st.session_state.feedback = None

# -----------------------------
# IMAGE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("Upload Food Image", type=["jpg", "jpeg", "png"])

# Show image preview
if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", width=350)

# -----------------------------
# RUN PREDICTION
# -----------------------------
if st.button("Analyze Food"):
    if not uploaded_file:
        st.error("Please upload an image first.")
    else:
        with st.spinner("Processing..."):
            try:
                img_bytes = io.BytesIO()
                # Always send as JPEG to backend
                img.convert("RGB").save(img_bytes, format="JPEG")
                img_bytes.seek(0)

                files = {"image": ("food.jpg", img_bytes, "image/jpeg")}
                response = requests.post(API_URL, files=files, timeout=60)

                if response.status_code == 200:
                    st.session_state.api_result = response.json()
                    st.success("Prediction complete!")
                else:
                    st.error(f"API Error: {response.text}")
            except Exception as e:
                st.error(f"API connection error: {str(e)}")

# ------------------------------------------------------
# DISPLAY RESULTS (using session_state so slider works)
# ------------------------------------------------------
result = st.session_state.api_result

if result:
    top1 = result.get("top1", None)
    top5 = result.get("top5", [])
    nutrition = result.get("nutrition", None)

    # ==================================================
    # Prediction Section
    # ==================================================
    st.subheader("Top Prediction")

    if top1:
        label = top1["label"]
        conf = float(top1["confidence"])

        st.success(f"**{label}** — Confidence: **{conf:.4f}**")

        # Confidence bar (0–100)
        st.write("Model confidence level:")
        st.progress(int(conf * 100))

    # --------------------
    # Top-5 Predictions
    # --------------------
    if top5:
        st.subheader("Top-5 Predictions")

        # Nice table for Top-5
        top5_df = pd.DataFrame(top5)
        top5_df["confidence"] = top5_df["confidence"].astype(float).round(4)
        top5_df = top5_df.rename(columns={"label": "Label", "confidence": "Confidence"})
        st.dataframe(top5_df, use_container_width=True)

    # ==================================================
    # Nutrition Info (Per 100g)
    # ==================================================
    st.subheader("Nutrition Information (Per 100g)")

    if nutrition:
        # Show raw 100g nutrition
        base_df = pd.DataFrame([nutrition])
        base_df = base_df.rename(
            columns={
                "description": "Description",
                "calories": "Calories",
                "protein": "Protein (g)",
                "fat": "Fat (g)",
                "carbohydrates": "Carbs (g)",
            }
        )
        st.dataframe(base_df, use_container_width=True)

        # -------------------------------
        # Serving Size Slider
        # -------------------------------
        st.info("⚠️ Values above are for **100g**. Adjust serving size below.")

        serving = st.slider(
            "Select serving size (grams):",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
        )

        factor = serving / 100.0

        def scale_value(x):
            import math

            if x is None:
                return None
            try:
                if pd.isna(x):
                    return None
            except Exception:
                pass
            return round(float(x) * factor, 2)

        adjusted_nutrition = {
            "Calories": scale_value(nutrition.get("calories")),
            "Protein (g)": scale_value(nutrition.get("protein")),
            "Fat (g)": scale_value(nutrition.get("fat")),
            "Carbs (g)": scale_value(nutrition.get("carbohydrates")),
        }

        st.subheader(f" Nutrition for {serving} g")
        adj_df = pd.DataFrame([adjusted_nutrition])
        st.dataframe(adj_df, use_container_width=True)
        
        # -------------------------------
        # Macro Breakdown Chart
        # -------------------------------
        st.subheader("Macro Breakdown")

        macros = {
            "Calories": adjusted_nutrition["Calories"],
            "Carbs (g)": adjusted_nutrition["Carbs (g)"],
            "Fat (g)": adjusted_nutrition["Fat (g)"],
            "Protein (g)": adjusted_nutrition["Protein (g)"],
        }

        chart_df = pd.DataFrame({
            "Macro": list(macros.keys()),
            "Grams": list(macros.values())
        })

        fig = px.pie(chart_df, names="Macro", values="Grams")
        st.plotly_chart(fig, use_container_width=True)


    else:
        st.warning("No nutrition data found for this food.")

    # ==================================================
    # Feedback Mechanism
    # ==================================================

    st.subheader("Feedback")
    st.write("Was this prediction helpful or accurate?")

    # Create session state holders
    if "feedback_type" not in st.session_state:
        st.session_state.feedback_type = None
    if "comment" not in st.session_state:
        st.session_state.comment = ""

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Yes"):
            st.session_state.feedback_type = "yes"
    with col2:
        if st.button("👎 No"):
            st.session_state.feedback_type = "no"

    # Only show comment box after user selects Yes/No
    if st.session_state.feedback_type:
        st.session_state.comment = st.text_area(
            "Optional: Tell us more (e.g., 'correct dish', 'calories seem high')",
            value=st.session_state.comment
        )

    # Submit button
    if st.button("Submit Feedback"):
        feedback_payload = {
            "prediction": top1,
            "nutrition": nutrition,
            "feedback_type": st.session_state.feedback_type,
            "comment": st.session_state.comment,
        }

        try:
            resp = requests.post("http://backend:3000/feedback", json=feedback_payload)
            if resp.status_code == 200:
                st.success("Thanks for your feedback! It helps improve CalTrackAI.")
            else:
                st.error("Failed to store feedback. Backend error.")
        except Exception as e:
            st.error(f"Could not send feedback: {e}")



else:
    st.info("Upload an image and click **Analyze Food** to see predictions and nutrition.")
