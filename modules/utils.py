# modules/utils.py

import requests

# Define constant for the root URL
API_ROOT_URL = 'https://manage-roborakhwala.com/v1api/'

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

# Function to call the user registration API
def user_registry(mobile, password, confirm_password):
    if password != confirm_password:
        return {"success": False, "message": "Passwords do not match"}
    
    try:
        url = f'{API_ROOT_URL}/user_registry'
        payload = {'mobile': mobile, 'password': password, 'confirm_password': confirm_password}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()  # Assuming the API returns a success message
        else:
            return {"success": False, "message": "Registration failed"}
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
