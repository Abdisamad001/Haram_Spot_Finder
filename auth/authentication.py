import streamlit as st
from auth.db import create_users_table, add_user, authenticate_user, add_admin, add_staff
from auth.db import check_contact_exists

# Thumbnail
st.markdown("<h1 style='text-align: center;'> 🕋 Welcome To Haram Available Spot Detection</h1>", unsafe_allow_html=True)
st.markdown("---")
if not st.session_state.get("logged_in", False):
    try:
        st.image("src/thumbnail.png", use_column_width=True)  
    except:
        st.error("Image not found.")

def login_signup():
    create_users_table()
    
    # Initialize session states
    if "user_type" not in st.session_state:
        st.session_state["user_type"] = None
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    
    if not st.session_state.get("logged_in", False):
       
        #login/register

        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                menu = ["Login", "Register"]
                choice = st.selectbox("Menu", menu)

                if choice == "Login":
                    st.subheader("Login")
                    
                    # User type 
                    user_type_options = ["user", "admin", "haram_staff"]
                    selected_user_type = st.selectbox("Login as", user_type_options)
                    
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    login_button = st.button("Login")

                    if login_button:
                        if not username or not password:
                            st.error("Please enter both username and password")
                        else:
                            user_data = authenticate_user(username, password)
                            if user_data:
                                
                                # Check user type 
                                if user_data['user_type'] == selected_user_type:
                                    st.session_state["logged_in"] = True
                                    st.session_state["username"] = username
                                    st.session_state["user_type"] = user_data['user_type']
                                    st.session_state["user_id"] = user_data['id']
                                    
                                    st.success(f"Welcome {username} 👋 (Logged in as {user_data['user_type']})")
                                    st.rerun()
                                else:
                                    st.error(f"Access denied. Your account type is {user_data['user_type']}, not {selected_user_type}")
                            else:
                                st.error("Invalid username or password")

                elif choice == "Register":
                    st.subheader("Create New Account")
                    
                    # Add user type selection
                    reg_user_type = st.selectbox(
                        "Register as", 
                        ["user", "admin", "haram_staff"]
                    )
                    
                    new_user = st.text_input("Username")
                    new_pass = st.text_input("Password", type="password")
                    name = st.text_input("Name")
                    contact = st.text_input("Contact")
                    
                    # Additional fields based on user type
                    if reg_user_type == "admin":
                        authentication = st.selectbox("Authentication Level", ["IT Admim", "Haram Data Scientist", "DB Admin"])
                    
                    elif reg_user_type == "haram_staff":
                        staff_role = st.selectbox("Role", ["Gate Monitor", "Security"])
                        
                    register_button = st.button("Register")

                    if register_button:

                        # Validate required fields
                        if not new_user or not new_pass or not name or not contact:
                            st.error("All fields are required")
                        else:
                            try:
                                # Create user account
                                user_id = add_user(new_user, new_pass, name, contact)
                                
                                # Create role-specific record
                                if reg_user_type == "admin":
                                    add_admin(name, authentication, user_id)
                                    
                                elif reg_user_type == "haram_staff":
                                    add_staff(name, staff_role, contact, user_id)
                                
                                st.success(f"{reg_user_type.capitalize()} account created successfully!")
                                st.info("Go to Login Menu to login.")
                                
                            except Exception as e:
                                st.error(f"Registration failed: {str(e)}")
    
    # Logout button 
    if st.session_state.get("logged_in"):
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.session_state["user_type"] = None
            st.session_state["user_id"] = None
            st.rerun()