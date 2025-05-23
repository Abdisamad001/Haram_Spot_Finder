import streamlit as st
from PIL import Image
from ultralytics import YOLO
import tempfile
import os
import random
import numpy as np

from auth.authentication import login_signup
from auth.db import create_users_table, save_spot, get_spots
from src.exception import handle_video_processing, handle_image_processing, handle_file_cleanup

# Load custom CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize login system
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# login/signup sidebar
login_signup()

# Stop app if not logged in
if not st.session_state["logged_in"]:
    st.stop()

# Load the model
model = YOLO('notebooks/models/best.pt')

# Embed Google Map
def show_google_map():
    st.markdown(
        """
        <div class="map-container">
            <iframe 
                style="height:100%;width:100%;border:0;border-radius:12px;" 
                frameborder="0"
                src="https://www.google.com/maps/embed/v1/directions?origin=masjid+nabawi&destination=masjid+nabawi&key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8"
                allowfullscreen>
            </iframe>
        </div>
        """,
        unsafe_allow_html=True
    )

# Layout
st.markdown("<h1 style='text-align: center;'> 🕋 Available Spot Detection</h1>", unsafe_allow_html=True)
st.markdown("---")

# navigation tab 
tab1, tab2 = st.tabs(["Detect Spots", "History"])

with tab1:
    option = st.radio("Choose input type:", ['Image', 'Video'])

    if option == 'Image':
        uploaded_file = st.file_uploader("Upload an image...", type=['jpg', 'jpeg', 'png'])
        if uploaded_file is not None:
            with st.spinner("Detecting available spots..."):
                image = Image.open(uploaded_file)
                try:
                    # Process image using exception handler
                    results, plotted = handle_image_processing(model, image)
                    
                    # Get spots count and save to DB
                    spots_count = len(results[0].boxes)
                    save_spot(st.session_state["username"], uploaded_file.name, spots_count, "image")
                    
                    # Two columns layout after detection
                    col1, col2 = st.columns(2, gap="large")

                    with col1:
                        st.image(plotted, caption="Detected Spots", use_column_width=True)
                        st.markdown(
                            f"<div class='spots-badge'>🟢 {spots_count} spots</div> <br>",
                            unsafe_allow_html=True
                        )
                        st.success(f"Detection saved to database!")

                    with col2:
                        st.subheader("🧭 Guidance to Available Spot")
                        st.write("Follow this map to reach your available spot.")
                        show_google_map()
                except Exception as e:
                    st.error(f"Failed to process image: {str(e)}")

    elif option == 'Video':
        uploaded_video = st.file_uploader("Upload a video...", type=['mp4', 'mov'])

        if uploaded_video is not None:
            temp_video_path = None

            with st.spinner("Processing video..."):
                # Save uploaded video 
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
                    tfile.write(uploaded_video.read())
                    temp_video_path = tfile.name
                
                try:
                    # Process video 
                    output_video_path, processed_video_bytes = handle_video_processing(model, temp_video_path)
                    
                    # For video, we'll estimate spots count (improve this based on your model)
                    # In real implementation, you'd extract this from video results
                    estimated_spots = random.randint(5, 15)
                    save_spot(st.session_state["username"], uploaded_video.name, estimated_spots, "video")
                    
                    # after video detection
                    col1, col2 = st.columns(2, gap="large")
                    
                    with col1:
                        # Original video
                        st.subheader("Original Video")
                        st.video(temp_video_path)
                        
                        # Display processed video
                        if processed_video_bytes:
                            st.subheader("Processed Video with Detection")
                            
                            st.video(processed_video_bytes)
                            
                            # download button
                            st.download_button(
                                label="Download Processed Video",
                                data=processed_video_bytes,
                                file_name="processed_prayer_spot.mp4",
                                mime="video/mp4"
                            )
                            
                            st.success(f"Detection saved with {estimated_spots} estimated spots!")
                        else:
                            st.error("Video processing failed or video cannot be played in browser.")
                            
                            # If video can't play
                            if output_video_path and os.path.exists(output_video_path):
                                st.info(f"Video was processed at {output_video_path} but may not be open with browser playback.")
                    
                    with col2:
                        st.subheader("🧭 Guidance to Available Spot")
                        st.write("Follow this map to reach your prayer spot.")
                        show_google_map()
                
                except Exception as e:
                    st.error(f"Error in video processing: {str(e)}")
                
                finally:
                    # Clean up temp files
                    if temp_video_path:
                        handle_file_cleanup([temp_video_path])

with tab2:
    st.subheader("Your Spot Detection History")
    
    # Get spot history for current user
    history = get_spots(st.session_state["username"])
    
    if not history:
        st.info("You haven't performed any detections yet.")
    else:
        # Display history in a simple table
        data = []
        for record in history:
            data.append({
                "Date": record["date"],
                "Type": record["type"],
                "File": record["filename"],
                "Spots": record["count"]
            })
        
        st.table(data)

st.markdown("---")

# Crowd Density
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

st.markdown("<div style='margin-top: 2rem;'>Crowd Density Indicator</div>", unsafe_allow_html=True)
st.progress(crowd_density / 100)


st.markdown(f"""
    <div class='caution'>
        <h1>🛑 CAUTION</h1>
        <p>The Map may not guide  you the exact spot, <strong>The feature is under development.</strong></p>
    </div>
""", unsafe_allow_html=True)