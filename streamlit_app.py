import streamlit as st
import requests

# Define constant for the root URL
API_ROOT_URL = 'https://manage-roborakhwala.com/v1api/'

# Function to make the login API call (separate login logic)
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

# Function to fetch IoT devices (separate device listing logic)
def get_iot_devices(mobile, jwt_token):
    try:
        url = f'{API_ROOT_URL}/get_user_profile_details'
        headers = {'Authorization': f'Bearer {jwt_token}'}
        payload = {'user_login_id': mobile, 'jwt_token': jwt_token}
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()  # Assuming the API returns a list of devices
        else:
            return {"success": False, "message": "Failed to fetch IoT devices"}
    except Exception as e:
        return {"success": False, "message": f"API request failed: {str(e)}"}

# Function to get device statuses on page load
def get_device_status(mobile, jwt_token):
    try:
        url = f'{API_ROOT_URL}/get_task'
        headers = {'Authorization': f'Bearer {jwt_token}'}
        payload = {'user_login_id': mobile, 'jwt_token': jwt_token}
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()  # Assuming the API returns a list of statuses
        else:
            return {"success": False, "message": "Failed to fetch device statuses"}
    except Exception as e:
        return {"success": False, "message": f"API request failed: {str(e)}"}

# Function to update the task (start/stop based on duration)
def update_task(device_id, jwt_token, mobile, duration):
    try:
        url = f'{API_ROOT_URL}/update_task'
        headers = {'Authorization': f'Bearer {jwt_token}'}
        payload = {
            'user_login_id': mobile,
            'jwt_token': jwt_token,
            'id': device_id,
            'duration': duration  # Duration > 0 = start, duration = 0 = stop
        }
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()  # Return the response containing the message
        else:
            return {"message": "Failed to execute device command"}
    except Exception as e:
        return {"message": f"API request failed: {str(e)}"}

# Injecting CSS styles at the top
st.markdown("""
    <style>
    .login-title {
        text-align: center;
        font-size: 24px;
        margin-bottom: 20px;
    }
    .device-name {
        text-align: center;
        font-size: 18px;
        margin: 10px 0;
    }
    .button-container {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Function to handle the login page UI and interaction
def login_page():
    st.markdown("<div class='login-title'>Robo Rakhwala</div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Login to your account</h3>", unsafe_allow_html=True)

    # Input fields for mobile number and password inside a form
    with st.form("login_form"):
        mobile = st.text_input("Mobile Number", placeholder="Enter your mobile number")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        login_button_clicked = st.form_submit_button("Login")  # Corrected to ensure button is inside the form

    # Perform login on button click
    if login_button_clicked:
        auth_response = login_api_call(mobile, password)

        # If login is successful, save jwt_token and mobile to session state
        if 'jwt_token' in auth_response:
            st.session_state['jwt_token'] = auth_response['jwt_token']
            st.session_state['mobile'] = mobile
            st.success("Login Successful! Redirecting to IoT device list...")
            st.rerun()
        else:
            st.error(auth_response.get('message', 'Login failed'))

# Function to display the IoT devices after login and provide start/stop controls
def iot_device_page():
    st.title("Your Registered Devices")

    # Get mobile and jwt_token from session state
    mobile = st.session_state.get('mobile')
    jwt_token = st.session_state.get('jwt_token')

    # Fetch the IoT devices using the API call
    if mobile and jwt_token:
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

                    st.markdown(f"<div class='device-name'>Device: {display_name} (Status: {device_status})</div>", unsafe_allow_html=True)

                    # Display start and stop buttons for each device
                    col1, col2 = st.columns(2)

                    with col1:
                        if device_status == 'STARTED':
                            st.button(f"Start {display_name}", key=f"start_{device_id}", disabled=True)
                            st.info(f"{display_name} is already started")
                        else:
                            if st.button(f"Start {display_name}", key=f"start_{device_id}"):
                                start_response = update_task(device_id, jwt_token, mobile, duration=30)  # Start for 30 minutes
                                st.success(start_response.get('message', 'Device started successfully!'))
                                st.rerun()

                    with col2:
                        if device_status == 'STOPPED':
                            st.button(f"Stop {display_name}", key=f"stop_{device_id}", disabled=True)
                            st.info(f"{display_name} is already stopped")
                        else:
                            if st.button(f"Stop {display_name}", key=f"stop_{device_id}"):
                                stop_response = update_task(device_id, jwt_token, mobile, duration=0)  # Stop the device
                                st.success(stop_response.get('message', 'Device stopped successfully!'))
                                st.rerun()

                    st.write("<br>", unsafe_allow_html=True)  # Add spacing between devices
        else:
            st.write("No IoT devices found or invalid response format.")

    # Provide a logout button
    if st.button("Logout"):
        if 'jwt_token' in st.session_state:
            del st.session_state['jwt_token']
        if 'mobile' in st.session_state:
            del st.session_state['mobile']
        st.rerun()

# Main function to manage session state and display relevant content
def main():
    # If user is not logged in, show the login page
    if 'jwt_token' not in st.session_state:
        login_page()
    else:
        # If logged in, show the IoT device list page
        iot_device_page()

# Run the app
if __name__ == "__main__":
    main()
