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

# Add CSS and animation for login and device pages
def add_css():
    st.markdown("""
    <style>
    /* Common CSS for both pages */
    body {
        background-color: #f0f2f6;
        color: #333;
    }
    h1 {
        color: #333;
        font-size: 3rem;
        text-align: center;
    }
    .stTextInput > div > div {
        margin-bottom: 1rem;
    }

    /* Center the login form */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 80vh;
        flex-direction: column;
    }

    /* Login button animation */
    .login-button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        transition: background-color 0.3s ease-in-out, transform 0.3s ease-in-out;
    }

    .login-button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }

    /* Device page buttons */
    .device-button {
        padding: 10px 20px;
        font-size: 1.2rem;
        color: white;
        border: none;
        cursor: pointer;
        margin: 10px;
        transition: background-color 0.3s ease-in-out, transform 0.3s ease-in-out;
    }

    .start-button {
        background-color: #28a745;
    }

    .stop-button {
        background-color: #dc3545;
    }

    .device-button:hover {
        transform: scale(1.05);
    }

    .device-list {
        text-align: center;
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to handle the login page UI and interaction
def login_page():
    add_css()  # Apply CSS
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("Robo Rakhwala")

    # Input fields for mobile number and password
    mobile = st.text_input("Mobile Number")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login", key='login_button')

    # Perform login on button click
    if login_button:
        auth_response = login_api_call(mobile, password)

        # If login is successful, save jwt_token and mobile to session state
        if 'jwt_token' in auth_response:
            st.session_state['jwt_token'] = auth_response['jwt_token']
            st.session_state['mobile'] = mobile
            st.success("Login Successful! Redirecting to IoT device list...")

            # Redirect to device list page
            st.rerun()
        else:
            st.error(auth_response.get('message', 'Login failed'))

    st.markdown('</div>', unsafe_allow_html=True)

# Function to display the IoT devices after login and provide start/stop controls
def iot_device_page():
    add_css()  # Apply CSS
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

                    st.write(f"Device: {display_name} (Status: {device_status})")

                    # Display start and stop buttons for each device
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(f"Start {display_name}", key=f"start_{device_id}", css_class="device-button start-button"):
                            start_response = update_task(device_id, jwt_token, mobile, duration=30)  # Start for 30 minutes
                            st.success(start_response.get('message', 'Device started successfully!'))
                            st.rerun()  # Reload the page after starting

                    with col2:
                        if st.button(f"Stop {display_name}", key=f"stop_{device_id}", css_class="device-button stop-button"):
                            stop_response = update_task(device_id, jwt_token, mobile, duration=0)  # Stop the device
                            st.success(stop_response.get('message', 'Device stopped successfully!'))
                            st.rerun()  # Reload the page after stopping

                    st.write("---")
        else:
            st.write("No IoT devices found or invalid response format.")

    # Provide a logout button
    if st.button("Logout"):
        # Clear session state on logout safely
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

