import streamlit as st
from PIL import Image
from ultralytics import YOLO
import tempfile
import os
import random  
from auth.authentication import login_signup  
from auth.db import create_users_table

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
                    image = Image.open(uploaded_file)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                        image.save(temp_file.name)
                        results = model(temp_file.name, save=True)

                        output_path = os.path.join(results[0].save_dir, os.path.basename(temp_file.name))
                        st.image(output_path, caption="Detected", use_container_width=True)

        elif option == 'Video':
            uploaded_video = st.file_uploader("Upload a video...", type=['mp4', 'mov', 'avi'])
            if uploaded_video is not None:
                with st.spinner("Processing video..."):
                    tfile = tempfile.NamedTemporaryFile(delete=False)
                    tfile.write(uploaded_video.read())

                    results = model(tfile.name, save=True)
                    st.video(tfile.name)
                    st.success("Video processed.")

    with col2:
        # Simulated crowd density
        st.markdown("###  🧍`Crowd Density`")
        crowd_density = random.randint(60, 100)
        st.metric(label="Density", value=f"{crowd_density} %")
