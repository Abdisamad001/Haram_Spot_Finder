import streamlit as st
from PIL import Image
from ultralytics import YOLO
import tempfile
import os
import random  # For fake crowd density

# Load the model
model = YOLO('notebooks/models/best.pt')

st.title("🕌 Available Spot Detection")

# Upload image or video
option = st.radio("Choose input type:", ['Image', 'Video'])

if option == 'Image':
    uploaded_file = st.file_uploader("Upload an image...", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        with st.spinner("Detecting available spots..."):
            # Save image temporarily
            image = Image.open(uploaded_file)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                image.save(temp_file.name)
                results = model(temp_file.name, save=True)

                # Display the output
                output_path = results[0].save_dir + "/" + os.path.basename(temp_file.name)
                st.image(output_path, caption="Detected", use_column_width=True)

                # Simulated crowd density
                crowd_density = random.randint(60, 100)  # Fake percentage between 60% and 100%
                st.metric("🧍 Crowd Density", f"{crowd_density} %")

elif option == 'Video':
    uploaded_video = st.file_uploader("Upload a video...", type=['mp4', 'mov', 'avi'])
    if uploaded_video is not None:
        with st.spinner("Processing video..."):
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_video.read())

            results = model(tfile.name, save=True)

            st.video(tfile.name)
            st.success("Video processed.")

            # Simulated crowd density
            crowd_density = random.randint(60, 100)
            st.metric("🧍 Crowd Density", f"{crowd_density} %")
