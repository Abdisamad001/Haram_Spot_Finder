import streamlit as st
from PIL import Image
from ultralytics import YOLO
import tempfile
import os
import random  
from auth.authentication import login_signup  
from auth.db import create_users_table
import cv2
import numpy as np

# Initialize login system
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Display login/signup sidebar
login_signup()

# Stop app if not logged in
if not st.session_state["logged_in"]:
    st.stop()

# Load the model
model = YOLO('notebooks/models/best.pt')

# Layout container
with st.container():
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title("🕌 Available Spot Detection")
        option = st.radio("Choose input type:", ['Image', 'Video'])

        if option == 'Image':
            uploaded_file = st.file_uploader("Upload an image...", type=['jpg', 'jpeg', 'png'])
            if uploaded_file is not None:
                with st.spinner("Detecting available spots..."):
                    # Read image directly to memory
                    image = Image.open(uploaded_file)
                    img_array = np.array(image)
                    
                    # Perform prediction without saving
                    results = model.predict(img_array, save=False, imgsz=640)
                    
                    # Display results directly
                    plotted = results[0].plot()  # Get plotted image with boxes
                    st.image(plotted, caption="Detected", use_column_width=True)

        elif option == 'Video':
            uploaded_video = st.file_uploader("Upload a video...", type=['mp4', 'mov', 'avi'])
            if uploaded_video is not None:
                with st.spinner("Processing video..."):
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as tfile:
                        tfile.write(uploaded_video.read())
                        
                        # Video prediction (still needs temporary file)
                        results = model.predict(tfile.name, save=False, stream=True)
                        
                        # Display original video (or process frames similarly to image)
                        st.video(tfile.name)
                        st.success("Video processed.")

    with col2:
        # Simulated crowd density
        st.markdown("###  🧍`Crowd Density`")
        crowd_density = random.randint(60, 100)
        st.metric(label="Density", value=f"{crowd_density} %")