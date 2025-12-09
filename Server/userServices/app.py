import secrets
import string
from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
import json
from flask_jwt_extended import jwt_required
import requests
from userHelper import userHelper
from modeles.role import ROLE

load_dotenv()
HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}
app = Flask(__name__)
SAVING_server = os.getenv('SAVING_server')


@app.route('/register-user', methods=['POST'])
def register_user():
    """
    Handle user registration from authService
    - Receives user data from authService
    - Validates manager code if provided
    - Adds user to manager's employees list if valid code
    - Saves user to Saving Server
    """
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'employee')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        address = data.get('address')
        department = data.get('department')
        user_id = data.get('userID')
        date_of_birth = data.get('date_of_birth')
        manager_code = data.get('managercode')
        
        # Validate required fields
        if not all([email, user_id]):
            return jsonify({"error": "Missing required fields: email and userID are required"}), 400
        
        # Prepare user data for Saving Server
        user_data = {
            "email": email,
            "password": password,
            "role": role,
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "department": department,
            "userID": user_id,
            "date_of_birth": date_of_birth,
            "employeesList": []
        }
        
        manager_email = None
        
        # If manager code is provided, validate it and get the manager
        if manager_code and manager_code.strip():
            manager_info = userHelper.validate_and_get_manager_by_code(manager_code)
            if manager_info:
                manager_email = manager_info.get('manager_email')
                print(f"✅ Valid manager code. User {email} will be added to manager {manager_email}'s team")
            else:
                print(f"⚠️ Invalid manager code provided: {manager_code}. Proceeding without manager assignment.")
        
        # Save user to Saving Server
        try:
            response = requests.post(
                f"{SAVING_server}/users/",
                json=user_data,
                headers=HEADERS,
                timeout=10
            )
            
            if response.status_code not in [200, 201]:
                return jsonify({"error": "Failed to save user to database", "details": response.text}), 500
                
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Database communication error: {str(e)}"}), 503
        
        # If we have a valid manager, add the new user to manager's employees list
        if manager_email:
            success = userHelper.add_employee_to_manager(manager_email, email)
            if success:
                print(f"✅ Successfully added {email} to {manager_email}'s employees list")
                # Mark the invite code as used
                userHelper.mark_invite_code_as_used(manager_code, email)
            else:
                print(f"⚠️ Failed to add {email} to {manager_email}'s employees list")
        
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "email": email,
            "manager_assigned": manager_email is not None,
            "manager_email": manager_email
        }), 201
        
    except Exception as e:
        print(f"❌ Error in register_user: {e}")
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@app.route('/users/by-email/<email>', methods=['GET'])
def get_user_by_email(email):
    """Get user details by email"""
    try:
        user = userHelper.getUserByEmail(email)
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/users/<email>/teammates', methods=['GET'])
def get_teammates(email):
    """
    Get all teammates of an employee (other employees under the same manager).
    
    Query Parameters:
        - include_details (bool): If true, returns full user objects instead of just emails
        - include_manager (bool): If true, includes manager information in response
    
    Returns:
        JSON with teammates list and optional manager info
    """
    try:
        # Parse query parameters
        include_details = request.args.get('include_details', 'false').lower() in ['true', '1', 'yes']
        include_manager = request.args.get('include_manager', 'false').lower() in ['true', '1', 'yes']
        
        # Get teammates using helper
        result = userHelper.get_teammates(email, include_details, include_manager)
        
        if not result.get("success", False) and result.get("error") == "Employee not found":
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error in get_teammates: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/users/<email>/team', methods=['GET'])
def get_full_team(email):
    """
    Get complete team information including the employee, their manager, and all teammates.
    
    Returns:
        JSON with full team information including employee, manager, and all teammates with details
    """
    try:
        # Get full team using helper
        result = userHelper.get_full_team(email)
        
        if not result.get("success", False) and result.get("error") == "Employee not found":
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error in get_full_team: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


   
@app.route('/getCodeForManager', methods=['POST'])
def getCode():
    """
    Handle code generation for manager
    - Verify current user is HR/Manager
    - Verify target user exists
    - Generate code
    - Save to Saving Server
    """
    try:
        data = request.get_json()
        manager_email = data.get('manager_email')

        manager_user = userHelper.getUserByEmail(manager_email)
        if manager_user is None:
            return jsonify({"Text": "Manager not found"}), 404
        
        # 3. Generate code
        code = userHelper.generateCode()
        print("el code : ",code)
        # 4. Save code to Saving Server
        payload = {
            "manager_id": manager_user.ID,
            "code": code,
            "max_uses": 1
        }
        
        userHelper.saveIntoSavingServer(payload,"managerCode")

        return jsonify({'code':code})
        

    except requests.exceptions.RequestException as e:
        return jsonify({"Text": f"Database communication error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"Text": f"Internal error: {str(e)}"}), 500


@app.route("/generateBecameManagerCode",methods=['GET'])
def becameManagerCode():
    code = userHelper.generateCode()
    payload= {
        'hrid':(request.get_json()).get("hrid"),
        'code':code,
        'max_uses':1
    }
    userHelper.saveIntoSavingServer(payload,"becameManagerCode")
    return jsonify({'code':code})

@app.route("/becameManger",methods=['POST'])
def becameManager():
    data= request.get_json()
    code=data.get("code")
    userMail=data.get("userMail")
    return jsonify ({"response":userHelper.make_employee_manager(code,userMail)})
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7052, debug=False)

