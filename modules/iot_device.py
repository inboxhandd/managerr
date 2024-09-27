import streamlit as st
import time
from modules.utils import API_ROOT_URL, get_iot_devices, get_device_status, update_task  # Import functions

# Loader CSS (can be injected globally)
LOADER_CSS = """
    <style>
    .loader {
        border: 16px solid #f3f3f3;
        border-radius: 50%;
        border-top: 16px solid #3498db;
        width: 120px;
        height: 120px;
        animation: spin 2s linear infinite;
        margin: auto;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .button {
        background-color: #3498db; /* Blue */
        border: none;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    .button:hover {
        background-color: #2980b9; /* Darker blue */
    }
    .device-name {
        font-weight: bold;
        margin: 5px 0;
    }
    .device-status {
        font-size: 14px;
        color: #555;
    }
    </style>
"""



# Function to show loader while page is processing
def show_loader():
    st.markdown(LOADER_CSS, unsafe_allow_html=True)
    st.markdown('<div class="loader"></div>', unsafe_allow_html=True)

# Function to make the login API call
def login_api_call(mobile, password):
    try:
        url = f'{API_ROOT_URL}/validate_user'
        payload = {'mobile': mobile, 'password': password}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()  # Assuming the API returns a jwt_token on success
        else:
            return {"success": False, "message": "Invalid mobile number or password"}
    except Exception as e:
        return {"success": False, "message": f"API request failed: {str(e)}"}

# Function to display the IoT devices after login and provide start/stop controls
def iot_device_page():
    st.title("Your Registered Devices")

    # Get mobile and jwt_token from session state
    mobile = st.session_state.get('mobile')
    jwt_token = st.session_state.get('jwt_token')

    # Fetch the IoT devices using the API call
    devices_response = get_iot_devices(mobile, jwt_token)
    status_response = get_device_status(mobile, jwt_token)  # Fetch device statuses on page load

    if 'message' in devices_response:
        st.error(devices_response['message'])
    elif isinstance(devices_response, list):  # Assuming the devices are returned as a list
        if 'message' in status_response:
            st.error(status_response['message'])
        elif isinstance(status_response, list):  # Assuming statuses are returned as a list
            for device in devices_response:
                device_label = device.get('device_label')
                device_id = device['id']
                display_name = device_label if device_label else device_id  # Show device_label or device_id

                # Get the status from the `get_task` API response
                device_status = next((status['action'] for status in status_response if status['id'] == device_id), 'UNKNOWN')

                st.markdown(f"<div class='device-name'>Device: {display_name}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='device-status'>Status: {device_status}</div>", unsafe_allow_html=True)

                # Display start and stop buttons for each device
                col1, col2 = st.columns(2)

                with col1:
                    if device_status == 'STARTED':
                        st.markdown(f"""
                            <button class='button' disabled>Start {display_name}</button>
                            <p>{display_name} is already started</p>
                        """, unsafe_allow_html=True)
                    else:
                        if st.button(f"Start {display_name}", key=f"start_{device_id}"):
                            # Show loading spinner immediately
                            show_loader()
                            start_response = update_task(device_id, jwt_token, mobile, duration=30)  # Start for 30 minutes
                            st.success(start_response.get('message', 'Device started successfully!'))
                            st.rerun()  # Refresh the page to update statuses

                with col2:
                    if device_status == 'STOPPED':
                        st.markdown(f"""
                            <button class='button' disabled>Stop {display_name}</button>
                            <p>{display_name} is already stopped</p>
                        """, unsafe_allow_html=True)
                    else:
                        if st.button(f"Stop {display_name}", key=f"stop_{device_id}"):
                            # Show loading spinner immediately
                            show_loader()
                            stop_response = update_task(device_id, jwt_token, mobile, duration=0)  # Stop the device
                            st.success(stop_response.get('message', 'Device stopped successfully!'))
                            st.rerun()  # Refresh the page to update statuses

                st.write("<br>", unsafe_allow_html=True)  # Add spacing between devices
    else:
        st.write("No IoT devices found or invalid response format.")

    # Provide a logout button
    if st.button("Logout"):
        if 'jwt_token' in st.session_state:
            del st.session_state['jwt_token']
        if 'mobile' in st.session_state:
            del st.session_state['mobile']
        st.rerun()  # Refresh the page after logout
