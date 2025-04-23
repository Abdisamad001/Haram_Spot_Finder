import streamlit as st
from PIL import Image
from ultralytics import YOLO
import tempfile
import os
import random
import cv2
import numpy as np

from auth.authentication import login_signup
from auth.db import create_users_table

# Load custom CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize login system
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Display login/signup sidebar
login_signup()

# Stop app
if not st.session_state["logged_in"]:
    st.stop()

# Load the model
model = YOLO('notebooks/models/best.pt')

# Layout container with two equal columns
with st.container():
    st.markdown("<h1 style='text-align: center;'> 🕋 Available Spot Detection</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
       
        option = st.radio("Choose input type:", ['Image', 'Video'])

        if option == 'Image':
            uploaded_file = st.file_uploader("Upload an image...", type=['jpg', 'jpeg', 'png'])
            if uploaded_file is not None:
                with st.spinner("Detecting available spots..."):
                    image = Image.open(uploaded_file)
                    img_array = np.array(image)
                    results = model.predict(img_array, save=False, imgsz=640)
                    plotted = results[0].plot()
                    st.image(plotted, caption="Detected", use_column_width=True)
                    st.markdown(
                        f"<div class='spots-badge'>🟢 {len(results[0].boxes)} spots</div>",
                        unsafe_allow_html=True
                    )

        elif option == 'Video':
            uploaded_video = st.file_uploader("Upload a video...", type=['mp4', 'mov', 'avi'])
            if uploaded_video is not None:
                with st.spinner("Processing video..."):
                    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as tfile:
                        tfile.write(uploaded_video.read())
                        results = model.predict(tfile.name, save=False, stream=True)
                        st.video(tfile.name)
                        st.success("Video processed.")

    with col2:
        st.markdown("<h3 style='color:#10B981;'>🧍 Crowd Density</h3>", unsafe_allow_html=True)
        crowd_density = random.randint(60, 100)

        if crowd_density > 80:
            color = "#EF4444"
            status = "high crowd"
        elif crowd_density >= 60:
            color = "#F59E0B"
            status = "warning"
        else:
            color = "#10B981"
            status = "good"

        st.markdown(f"""
            <div class='status-card {status}'>
                <h1 style='font-size: 4rem; color: {color};'>{crowd_density}%</h1>
                <p style='color: #9CA3AF;'>Current estimated crowd density</p>
            </div>
        """, unsafe_allow_html=True)

        # crowd density bar 
        st.markdown("<div style='margin-top: 2rem;'>Crowd Density Indicator</div>", unsafe_allow_html=True)
        st.progress(crowd_density / 100)