# main.py

import streamlit as st
from modules.login import login_page, registration_page
from modules.iot_device import iot_device_page

# Initialize session state for page toggle if not already set
if 'show_registration_page' not in st.session_state:
    st.session_state['show_registration_page'] = False

# Main function to manage session state and display relevant content
def main():
    # If user is not logged in, show the login page or registration page
    if 'jwt_token' not in st.session_state:
        if st.session_state['show_registration_page']:
            registration_page()
        else:
            login_page()
    else:
        # If logged in, show the IoT device list page
        iot_device_page()

# Run the app
if __name__ == "__main__":
    main()
