from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
import json
import requests
from Helper import authHelper
from supaBase.supaBase import dataBaseAuth

load_dotenv()

app = Flask(__name__)
authenter = dataBaseAuth(os.getenv("SUPABASE_URL"),os.getenv("SUPABASE_KEY"))
auth_helper = authHelper(authenter)
SAVING_server = os.getenv('SAVING_server')
USER_SERVICE = os.getenv('userService')



@app.route("/signup",methods=['POST'])
def signUp():
    data = request.get_json()

    email = data.get('email')
    firstName = data.get('FirstName')
    lastName = data.get('LastName')
    Password = data.get('Password')
    DateOfBirth = data.get('DateOfBirth')
    address = data.get('Address')
    ManagerCode = data.get('managercode')

    # Create user in Supabase Auth
    result = auth_helper.CreateUser(email, Password)
    
    # Check if user creation failed
    if result is None:
        return jsonify({"error": "Failed to create user in authentication service"}), 500
    
    # Parse the result
    try:
        result = json.loads(result)
        Token = result.get("Token")
        id = result.get("id")
    except Exception as e:
        print(f"Error parsing auth result: {e}")
        return jsonify({"error": "Error processing authentication response"}), 500
    
    # Prepare user data for user service
    user_data = {
            "email": email,
            "password": Password,  
            "role": "employee",
            "first_name": firstName,
            "last_name": lastName,
            "address": address,
            "department": "hadhi n3amerha mba3ed",
            "userID": id,  
            "date_of_birth": DateOfBirth,
            "managercode": ManagerCode  # Pass the manager code to userService
        }

    try:
        # Send user data to UserService instead of directly to Saving Server
        response_from_user_service = requests.post(
            f'http://{USER_SERVICE}/register-user', 
            json=user_data,
            timeout=15
        )
    except Exception as e:
        delResult = auth_helper.deleteUser(id)
        return jsonify({"message": "error connecting to user service", "error": str(e), "del result": delResult}), 500

    if response_from_user_service.status_code == 200 or response_from_user_service.status_code == 201: 
        print("from app : user registered successfully via userService")
    
        return jsonify({
            "Token": result.get("Token"),
            "id": result.get("id")
        }), 200
    else:
        delResult = auth_helper.deleteUser(id)
        error_msg = "error registering user via user service"
        try:
            error_msg = response_from_user_service.json().get("error", error_msg)
        except:
            pass
        return jsonify({"message": error_msg, "del result": delResult}), 500
        

@app.route("/login",methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    Password = data.get('password')
    
    # Get result from auth helper
    login_result = auth_helper.login(email, Password)
    
    # Check if login_result is None (failed)
    if login_result is None:
        return jsonify({"error": "Login failed. Invalid credentials or service error."}), 401
    
    # Parse the JSON result
    try:
        result = json.loads(login_result)
        return jsonify({
            "Token": result.get("Token"),
            "firstname": result.get("firstname"),
            "lastname": result.get("lastname"),
            "role": result.get("role")
        }), 200
    except Exception as e:
        print(f"Error parsing login result: {e}")
        return jsonify({"error": "Error processing login response"}), 500


@app.route("/user/<user_id>/email", methods=['GET'])
def get_user_email(user_id):
    """Get user email by user ID - used by Gateway for JWT identity resolution"""
    try:
        result = auth_helper.getUserEmailById(user_id)
        
        if result is None:
            return jsonify({"error": "User not found"}), 404
        
        result = json.loads(result)
        return jsonify({
            "email": result.get("email"),
            "id": result.get("id")
        }), 200
    except Exception as e:
        print(f"Error getting user email: {e}")
        return jsonify({"error": "Error retrieving user email"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7051, debug=False)
