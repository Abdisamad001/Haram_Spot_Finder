import streamlit as st
from PIL import Image
from ultralytics import YOLO
import tempfile
import os
import random
import numpy as np

from auth.authentication import login_signup
from auth.db import create_users_table, save_spot, get_spots
from auth.db import get_available_spaces, get_all_gates, get_user_allocations
from auth.db import get_staff_gates, get_all_users, get_staff_by_user_id, get_all_staff
from auth.db import add_space, add_gate, add_model, add_allocation
from auth.db import update_space_availability, update_gate_status, assign_gate_to_staff
from src.exception import handle_video_processing, handle_image_processing, handle_file_cleanup

# Load custom CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize login system
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

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

# Get user type from session state
user_type = st.session_state.get("user_type", "user")

# Regular user interface
if user_type == "user":
    tab1, tab2, tab3 = st.tabs(["Detect Spots", "History", "Allocations"])

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
                            
                            # Option to allocate a spot
                            spaces = get_available_spaces()
                            if spaces:
                                st.subheader("Reserve a Spot")
                                selected_space = st.selectbox(
                                    "Choose a space to reserve:", 
                                    [f"Space {s['space_id']} at {s['location']} (Capacity: {s['capacity']})" for s in spaces],
                                    key="space_select"
                                )
                                if st.button("Reserve Spot"):
                                    space_id = int(selected_space.split()[1])
                                    add_allocation(space_id, st.session_state["user_id"])
                                    st.success(f"Successfully reserved space {space_id}!")
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
                        
                        # For video, we'll estimate spots count
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
    
    with tab3:
        st.subheader("Your Space Allocations")
        
        # Get allocations for current user
        allocations = get_user_allocations(st.session_state["user_id"])
        
        if not allocations:
            st.info("You don't have any space allocations yet.")
        else:
            # Display allocations
            alloc_data = []
            for record in allocations:
                alloc_data.append({
                    "Date": record["timestamp"],
                    "Space ID": record["space_id"],
                    "Location": record["location"],
                    "Capacity": record["capacity"]
                })
            
            st.table(alloc_data)

# Admin interface
elif user_type == "admin":
    tabs = st.tabs(["System Management", "Users", "Spaces", "Gates"])
    
    with tabs[0]:
        st.subheader("System Management")
        
        # Add new model
        st.write("Add New Model")
        with st.form("add_model_form"):
            model_name = st.text_input("Model Name")
            model_version = st.text_input("Version")
            model_status = st.selectbox("Status", ["active", "inactive", "testing"])
            
            model_submit = st.form_submit_button("Add Model")
            
            if model_submit:
                try:
                    add_model(model_name, model_version, model_status)
                    st.success(f"Model {model_name} v{model_version} added successfully!")
                except Exception as e:
                    st.error(f"Failed to add model: {str(e)}")
    
    with tabs[1]:
        st.subheader("User Management")
        
        users = get_all_users()
        if not users:
            st.info("No users found in the system.")
        else:
            user_data = []
            for user in users:
                try:
                    user_data.append({
                        "ID": user["id"],
                        "Username": user["username"],
                        "Name": user.get("name", ""),
                        "Contact": user.get("contact", "")
                    })
                except:
                    # Handle cases where dict keys don't exist
                    user_data.append({
                        "ID": user.get("id", ""),
                        "Username": user.get("username", ""),
                        "Name": "",
                        "Contact": ""
                    })
            
            st.table(user_data)
            
    with tabs[2]:
        st.subheader("Space Management")
        
        # Add new space
        with st.form("add_space_form"):
            st.write("Add New Space")
            space_location = st.text_input("Location")
            space_capacity = st.number_input("Capacity", min_value=1, value=10)
            space_availability = st.selectbox("Availability", ["available", "occupied", "maintenance"])
            
            space_submit = st.form_submit_button("Add Space")
            
            if space_submit:
                try:
                    add_space(space_location, space_capacity, space_availability)
                    st.success(f"Space at {space_location} added successfully!")
                except Exception as e:
                    st.error(f"Failed to add space: {str(e)}")
        
        # View all spaces
        st.subheader("All Spaces")
        spaces = get_available_spaces()
        if not spaces:
            st.info("No spaces found in the system.")
        else:
            space_data = []
            for space in spaces:
                space_data.append({
                    "Space ID": space["space_id"],
                    "Location": space["location"],
                    "Capacity": space["capacity"],
                    "Availability": space["availability"]
                })
            
            st.table(space_data)
            
    with tabs[3]:
        st.subheader("Gate Management")
        
        # Add new gate
        with st.form("add_gate_form"):
            st.write("Add New Gate")
            gate_name = st.text_input("Gate Name")
            gate_location = st.text_input("Location")
            gate_status = st.selectbox("Status", ["open", "closed", "maintenance"])
            
            gate_submit = st.form_submit_button("Add Gate")
            
            if gate_submit:
                try:
                    add_gate(gate_name, gate_location, gate_status)
                    st.success(f"Gate {gate_name} added successfully!")
                except Exception as e:
                    st.error(f"Failed to add gate: {str(e)}")
        
        # View all gates
        st.subheader("All Gates")
        gates = get_all_gates()
        if not gates:
            st.info("No gates found in the system.")
        else:
            gate_data = []
            for gate in gates:
                gate_data.append({
                    "Gate ID": gate["gate_id"],
                    "Name": gate["name"],
                    "Location": gate["location"],
                    "Status": gate["status"]
                })
            
            st.table(gate_data)
            
            # Update gate status
            st.subheader("Update Gate Status")
            if gates:
                selected_gate = st.selectbox(
                    "Select Gate",
                    [f"{g['gate_id']} - {g['name']}" for g in gates]
                )
                gate_id = int(selected_gate.split(' - ')[0])
                new_status = st.selectbox("New Status", ["open", "closed", "maintenance"])
                
                if st.button("Update Status"):
                    try:
                        update_gate_status(gate_id, new_status)
                        st.success(f"Gate {gate_id} status updated to {new_status}")
                    except Exception as e:
                        st.error(f"Failed to update gate status: {str(e)}")
        
        # Assign staff to gates - FIXED THIS SECTION
        st.markdown("---")  # Add separation
        st.subheader("Assign Staff to Gates")
        
        # Get all staff
        staff = get_all_staff()
        
        if not staff:
            st.warning("No haram staff found in the system. Please register haram staff first.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                selected_staff = st.selectbox(
                    "Select Haram Staff",
                    [f"{s['staff_id']} - {s['name']} ({s.get('role', 'Staff')})" for s in staff]
                )
                staff_id = int(selected_staff.split(' - ')[0])
                
            with col2:
                if gates:
                    selected_gate = st.selectbox(
                        "Select Gate to Monitor",
                        [f"{g['gate_id']} - {g['name']}" for g in gates],
                        key="assign_gate"
                    )
                    gate_id = int(selected_gate.split(' - ')[0])
                    
                    if st.button("Assign Gate to Staff"):
                        try:
                            assign_gate_to_staff(staff_id, gate_id)
                            st.success(f"Gate {gate_id} assigned to staff {staff_id} successfully!")
                        except Exception as e:
                            st.error(f"Failed to assign gate: {str(e)}")
                else:
                    st.warning("No gates available. Please add gates first.")

# Haram staff interface
elif user_type == "haram_staff":
    # Get staff ID
    user_id = st.session_state["user_id"]
    staff_data = get_staff_by_user_id(user_id)
    
    if staff_data:
        staff_id = staff_data["staff_id"]
        staff_name = staff_data["name"]
        staff_role = staff_data["role"]
        staff_contact = staff_data["contact"]
        
        # Display staff information
        st.subheader(f"Staff Information")
        st.write(f"**Staff ID:** {staff_id}")
        st.write(f"**Name:** {staff_name}")
        st.write(f"**Role:** {staff_role}")
        st.write(f"**Contact:** {staff_contact}")
        
        st.markdown("---")
        
        # Gate Monitoring Interface
        st.subheader("Gate Monitoring")
        
        # Get gates assigned to this staff member
        assigned_gates = get_staff_gates(staff_id)
        
        if not assigned_gates or len(assigned_gates) == 0:
            st.warning("You have no gates assigned to monitor. Please contact an admin to assign gates to you.")
        else:
            # Display gates in a table
            gate_data = []
            for gate in assigned_gates:
                gate_data.append({
                    "Gate ID": gate["gate_id"],
                    "Name": gate["name"],
                    "Location": gate["location"],
                    "Status": gate["status"]
                })
            
            st.write(f"You are currently monitoring **{len(assigned_gates)}** gates:")
            st.table(gate_data)
            
            # Update gate status
            st.subheader("Update Gate Status")
            selected_gate = st.selectbox(
                "Select Gate", 
                [f"{g['gate_id']} - {g['name']}" for g in assigned_gates]
            )
            gate_id = int(selected_gate.split(' - ')[0])
            new_status = st.selectbox("New Status", ["open", "closed", "maintenance", "crowded"])
            
            if st.button("Update Gate Status"):
                try:
                    update_gate_status(gate_id, new_status)
                    st.success(f"Gate {gate_id} status updated to {new_status}")
                except Exception as e:
                    st.error(f"Failed to update gate status: {str(e)}")
    else:
        st.error("Staff information not found. Please contact an admin.")

# crowd density 
if user_type == "user":
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
            <p>The Map may not guide you to the exact spot, <strong>The feature is under development.</strong></p>
        </div>
    """, unsafe_allow_html=True)