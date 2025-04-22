import streamlit as st
from auth.db import create_users_table, add_user, authenticate_user

def login_signup():
    create_users_table()
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        login_button = st.sidebar.button("Login")

        if login_button:
            if authenticate_user(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Welcome {username} 👋")
            else:
                st.error("Invalid username or password")

    elif choice == "Register":
        st.sidebar.subheader("Create New Account")
        new_user = st.sidebar.text_input("New Username")
        new_pass = st.sidebar.text_input("New Password", type="password")
        register_button = st.sidebar.button("Register")

        if register_button:
            try:
                add_user(new_user, new_pass)
                st.success("Account created successfully!")
                st.info("Go to Login Menu to login.")
            except:
                st.error("Username already exists.")
