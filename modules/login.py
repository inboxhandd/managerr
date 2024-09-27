# modules/login.py

import streamlit as st
from modules.utils import login_api_call, user_registry

# Function to handle the registration page UI and interaction
def registration_page():
    st.title("User Registration")

    # Input fields for mobile number, password, and confirm password
    with st.form("registration_form"):
        mobile = st.text_input("Mobile Number", placeholder="Enter your mobile number")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        submit_button_clicked = st.form_submit_button("Register")

    # Perform registration on form submission
    if submit_button_clicked:
        registration_response = user_registry(mobile, password, confirm_password)

        if registration_response.get('success'):
            st.success("Registration successful! Please login.")
            st.session_state['show_registration_page'] = False  # Redirect to login after successful registration
        else:
            st.error(registration_response.get('message', 'Registration failed'))
 # Add a 'Back' button to go back to the login page
    if st.button("Back to Login"):
        st.session_state['show_registration_page'] = False  # Redirect to the login page
        st.experimental_rerun()  # Force rerun to update the UI


# Function to handle the login page UI and interaction
def login_page():
    st.title("Robo Rakhwala Login")

    # Input fields for mobile number and password inside a form
    with st.form("login_form"):
        mobile = st.text_input("Mobile Number", placeholder="Enter your mobile number")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        login_button_clicked = st.form_submit_button("Login")

    # Perform login on button click
    if login_button_clicked:
        auth_response = login_api_call(mobile, password)

        # If login is successful, save jwt_token and mobile to session state
        if 'jwt_token' in auth_response:
            st.session_state['jwt_token'] = auth_response['jwt_token']
            st.session_state['mobile'] = mobile
            st.success("Login Successful! Redirecting to IoT device list...")
            st.rerun()  # Use the new rerun method
        else:
            st.error(auth_response.get('message', 'Login failed'))

    # Provide a link to the registration page
    if st.button("Register here", key="register_link"):
        st.session_state['show_registration_page'] = True  # Toggle to registration page
        st.rerun()  # Use the new rerun method to refresh the UI immediately