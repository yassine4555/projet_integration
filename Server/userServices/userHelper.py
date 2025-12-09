import secrets
import string
from flask import jsonify
import requests
import logging
import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Import models
from modeles.user import User
from modeles.role import ROLE
from modeles.department import Department

load_dotenv()

logger = logging.getLogger(__name__)


class userHelper:
    SAVING_SERVER_URL = os.getenv('SAVING_server')
    HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}
    
    @staticmethod
    def getUserByEmail(email: str) -> Optional[User]:
        """Get user by email from Saving Server"""
        try:
            user = userHelper.get_user_by_email_from_SavingServer(email)
            if user:
                logger.info(f"✅ User retrieved from Saving Server: {email}")
            else:
                logger.info(f"⚠️ User not found in Saving Server: {email}")
            return user
        except Exception as e:
            logger.error(f"❌ Error getting user by email from Saving Server: {e}")
            return None

    @staticmethod
    def get_user_by_email_from_SavingServer(email: str) -> Optional[User]:
        """
        Retrieve user from Saving Server by email
        Returns User object or None if not found
        """
        try:
            # Get all users from Saving Server
            
            response = requests.get(
                f"{userHelper.SAVING_SERVER_URL}/users/",
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get users from Saving Server: {response.status_code}")
                return None
            
            data = response.json()
            users = data.get("data", [])
            
            # Find user by email
            for user_data in users:
                if user_data.get("email", "").lower() == email.lower():
                    return userHelper._convert_server_user_to_internal(user_data)
            
            logger.info(f"User not found in Saving Server: {email}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting user from Saving Server: {e}")
            return None
    
    @staticmethod
    def _convert_role_from_server(server_role: str) -> ROLE:
        """Convert server role string to internal ROLE enum"""
        role_mapping = {
            "hr": ROLE.HR,
            "manager": ROLE.MANAGER,
            "employee": ROLE.EMPLOYER
        }
        return role_mapping.get(server_role.lower(), ROLE.GUEST)
    
    @staticmethod
    def _convert_department_from_server(dept_str: Optional[str]) -> Optional[Department]:
        """Convert server department string to internal DEPARTMENT enum"""
        if dept_str is None or dept_str == "":
            return None
        try:
            return Department[dept_str.upper()]
        except (KeyError, AttributeError):
            return None
    
    @staticmethod
    def _convert_server_user_to_internal(user_data: Dict[str, Any]) -> User:
        """
        Convert Saving Server user data to internal User object
        """
        user = User(
            Email=user_data.get("email", ""),
            FirstName=user_data.get("first_name", ""),
            LastName=user_data.get("last_name", ""),
            DateOfBirth=user_data.get("date_of_birth", ""),
            Address=user_data.get("address", "")
        )
        
        # Set ID (use userID if available, otherwise use server id as string)
        user.ID = user_data.get("userID", str(user_data.get("id", "")))
        
        # Set role
        user.Role = userHelper._convert_role_from_server(user_data.get("role", "employee"))
        
        # Set department
        user.Department = userHelper._convert_department_from_server(user_data.get("department"))
        
        # Set employees list (if manager)
        user.EmployeesList = user_data.get("employeesList", [])
        
        return user
    

    @staticmethod
    def generateCode():
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    @staticmethod
    def saveIntoSavingServer(data,args):
        try:
            save_operations = {
                "managerCode": userHelper._save_manager_code,
                "becameManagerCode": userHelper._save_became_manager_code
                # Add more operations here as needed
                
            }
            
            # Get the appropriate save function
            save_function = save_operations.get(args)
            
            if save_function is None:
                logger.error(f"❌ Unknown operation type: {args}")
                return False, {"error": f"Unknown operation: {args}"}, 400
            
            # Execute the save operation
            return save_function(data)
            
        except Exception as e:
            logger.error(f"❌ Error in saveIntoSavingServer: {e}")
            return False, {"error": str(e)}, 500

    @staticmethod
    def _save_manager_code(data):
        
        try:
           
            # Prepare payload
            payload = {
                "manager_id": data.get("manager_id"),
                "code": data.get("code"),
                "max_uses": data.get("max_uses", 1)  # Default to 1 if not provided
            }
            
            # Send request to Saving Server
            response = requests.post(
                f"{userHelper.SAVING_SERVER_URL}/invites/",
                json=payload,
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            # Check response
            if response.status_code in [200, 201]:
                logger.info(f"✅ Manager code saved successfully: {data.get('code')}")
                return True, response.json() if response.text else {"success": True}, response.status_code
            else:
                logger.error(f"❌ Failed to save manager code: {response.status_code}")
                return False, {"error": "Failed to save code to database"}, response.status_code
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error saving manager code: {e}")
            return False, {"error": f"Database communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"❌ Error saving manager code: {e}")
            return False, {"error": str(e)}, 500

    @staticmethod
    def _save_became_manager_code(data):
        
        try:
            
            # Prepare payload
            payload = {
                "hrid": data.get("hrid"),
                "code": data.get("code"),
                "max_uses": data.get("max_uses", 1)  # Default to 1 if not provided
            }
            
            # Send request to Saving Server
            response = requests.post(
                f"{userHelper.SAVING_SERVER_URL}/manager_codes/becameManagerCode",
                json=payload,
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            # Check response
            if response.status_code in [200, 201]:
                logger.info(f"✅ Manager code saved successfully: {data.get('code')}")
                return True, response.json() if response.text else {"success": True}, response.status_code
            else:
                logger.error(f"❌ Failed to save manager code: {response.status_code}")
                return False, {"error": "Failed to save code to database"}, response.status_code
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error saving manager code: {e}")
            return False, {"error": f"Database communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"❌ Error saving manager code: {e}")
            return False, {"error": str(e)}, 500
    
    @staticmethod
    def _convert_user_to_database_format(user: User, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert User object to database format matching required fields:
        ['email', 'first_name', 'last_name', 'role', 'department', 'address', 'date_of_birth', 'password']
        """
        # Convert role to lowercase string (database expects 'manager', 'employee', etc.)
        role_value = user.getRole().value.lower() if isinstance(user.getRole(), ROLE) else str(user.getRole()).lower()
        
        # Convert department to string or None
        department_value = user.getDepartment().value if user.getDepartment() else None
        
        database_user = {
            "email": user.getEmail(),
            "first_name": user.getFirstName(),
            "last_name": user.getLastName(),
            "role": role_value,
            "department": department_value,
            "address": user.getAddress(),
            "date_of_birth": user.getDateOfBirth(),
            "password": password if password else ""  # Empty string if password not provided
        }
        
        return database_user
    
    @staticmethod
    def make_employee_manager(code, userMail):
        if(userHelper.verify_became_manager_code(code)):
            employee = userHelper.get_user_by_email_from_SavingServer(userMail)
            if employee is None:
                return "user not found"
            
            employee.setRole(ROLE.MANAGER)
            
            # Convert to proper database format
            user_data = userHelper._convert_user_to_database_format(employee)
            
            userHelper.update_user(employee.getEmail(), user_data)
            return "done"
        else :
            return "invalid code"



    @staticmethod
    def update_user(user_id, user_data):
        try:
            response = requests.put(
                f"{userHelper.SAVING_SERVER_URL}/users/{user_id}",
                json=user_data,
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return True
            return False
                
        except Exception as e:
            logger.error(f"❌ Error updating user: {e}")
            return False
    @staticmethod
    def verify_became_manager_code(code):
        try:
            response = requests.get(
                f"{userHelper.SAVING_SERVER_URL}/manager_codes/becameManagerCode/{code}",
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            return False
                
        except Exception as e:
            logger.error(f"❌ Error verifying became manager code: {e}")
            return False

    @staticmethod
    def validate_and_get_manager_by_code(code: str) -> Optional[Dict[str, Any]]:
        """
        Validate a manager invite code and return the manager's information.
        Returns dict with manager_email and manager_id if valid, None otherwise.
        """
        try:
            # First, get the invite code details from Saving Server
            response = requests.get(
                f"{userHelper.SAVING_SERVER_URL}/invites/{code}",
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.info(f"⚠️ Invite code not found or invalid: {code}")
                return None
            
            invite_data = response.json()
            invite_data = invite_data.get("data")
            
            # Check if the code is still valid (not expired, not max uses reached)
            if not invite_data.get("is_active", False):
                logger.info(f"⚠️ Invite code is no longer active: {code}")
                return None
            
            used_count = invite_data.get("used_count", 0)
            max_uses = invite_data.get("max_uses", 1)
            if used_count >= max_uses:
                logger.info(f"⚠️ Invite code has reached max uses: {code}")
                return None
            
            manager_id = invite_data.get("manager_id")
            if not manager_id:
                logger.error(f"❌ Invite code has no manager_id: {code}")
                return None
            
            # Get manager's email from their user record
            manager_user = userHelper.get_user_by_id_from_SavingServer(manager_id)
            if manager_user:
                return {
                    "manager_id": manager_id,
                    "manager_email": manager_user.getEmail()
                }
            
            logger.error(f"❌ Manager not found for ID: {manager_id}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error validating invite code: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error validating invite code: {e}")
            return None

    @staticmethod
    def get_user_by_id_from_SavingServer(user_id: str) -> Optional[User]:
        """
        Retrieve user from Saving Server by user ID
        Returns User object or None if not found
        """
        try:
            response = requests.get(
                f"{userHelper.SAVING_SERVER_URL}/users/",
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get users from Saving Server: {response.status_code}")
                return None
            
            data = response.json()
            users = data.get("data", [])
            
            # Find user by userID
            for user_data in users:
                if user_data.get("userID") == user_id or str(user_data.get("id")) == str(user_id):
                    return userHelper._convert_server_user_to_internal(user_data)
            
            logger.info(f"User not found in Saving Server with ID: {user_id}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting user from Saving Server: {e}")
            return None

    @staticmethod
    def add_employee_to_manager(manager_email: str, employee_email: str) -> bool:
        """
        Add an employee email to a manager's employees list.
        Returns True if successful, False otherwise.
        """
        try:
            # First get the manager's current data
            manager = userHelper.get_user_by_email_from_SavingServer(manager_email)
            if not manager:
                logger.error(f"❌ Manager not found: {manager_email}")
                return False
            
            # Get current employees list
            current_employees = manager.EmployeesList if manager.EmployeesList else []
            
            # Check if employee is already in the list
            if employee_email in current_employees:
                logger.info(f"ℹ️ Employee {employee_email} already in manager's list")
                return True
            
            # Add the new employee
            current_employees.append(employee_email)
            
            # Update the manager's record
            update_data = {
                "employeesList": current_employees
            }
            
            response = requests.put(
                f"{userHelper.SAVING_SERVER_URL}/users/{manager_email}",
                json=update_data,
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Added {employee_email} to {manager_email}'s employees list")
                return True
            else:
                logger.error(f"❌ Failed to update manager's employees list: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error adding employee to manager: {e}")
            return False

    @staticmethod
    def mark_invite_code_as_used(code: str, used_by_email: str) -> bool:
        """
        Mark an invite code as used by incrementing its used_count.
        """
        try:
            response = requests.put(
                f"{userHelper.SAVING_SERVER_URL}/invites/{code}/use",
                json={"used_by_email": used_by_email},
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Marked invite code {code} as used by {used_by_email}")
                return True
            else:
                logger.warning(f"⚠️ Could not mark invite code as used: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error marking invite code as used: {e}")
            return False

    @staticmethod
    def get_all_users_from_SavingServer() -> list:
        """
        Retrieve all users from Saving Server
        Returns list of user data dictionaries
        """
        try:
            response = requests.get(
                f"{userHelper.SAVING_SERVER_URL}/users/",
                headers=userHelper.HEADERS,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get users from Saving Server: {response.status_code}")
                return []
            
            data = response.json()
            return data.get("data", [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting users from Saving Server: {e}")
            return []

    @staticmethod
    def find_manager_for_employee(employee_email: str) -> Optional[Dict[str, Any]]:
        """
        Find the manager who has this employee in their employees_list.
        Returns manager data dict or None if not found.
        """
        try:
            all_users = userHelper.get_all_users_from_SavingServer()
            
            for user_data in all_users:
                # Check if this user is a manager and has employees
                employees_list = user_data.get("employeesList", [])
                if employees_list and employee_email.lower() in [e.lower() for e in employees_list]:
                    return user_data
            
            logger.info(f"No manager found for employee: {employee_email}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding manager for employee: {e}")
            return None

    @staticmethod
    def get_teammates(employee_email: str, include_details: bool = False, include_manager: bool = False) -> Dict[str, Any]:
        """
        Get all teammates of an employee (other employees under the same manager).
        
        Args:
            employee_email: The email of the employee
            include_details: If True, return full user objects instead of just emails
            include_manager: If True, include manager information in response
            
        Returns:
            Dictionary with teammates information
        """
        try:
            # First verify the employee exists
            employee = userHelper.get_user_by_email_from_SavingServer(employee_email)
            if not employee:
                return {
                    "success": False,
                    "error": "Employee not found"
                }
            
            # Find the manager for this employee
            manager_data = userHelper.find_manager_for_employee(employee_email)
            
            if not manager_data:
                # No manager found
                result = {
                    "success": True,
                    "employee": employee_email,
                    "message": "No manager found for this employee",
                    "manager": None,
                    "teammates": [],
                    "teammates_count": 0
                }
                return result
            
            # Get all employees under this manager
            employees_list = manager_data.get("employeesList", [])
            
            # Filter out the requesting employee to get only teammates
            teammates_emails = [e for e in employees_list if e.lower() != employee_email.lower()]
            
            # Build response
            result = {
                "success": True,
                "employee": employee_email,
                "teammates_count": len(teammates_emails)
            }
            
            # Include manager info if requested
            if include_manager:
                result["manager"] = {
                    "email": manager_data.get("email"),
                    "first_name": manager_data.get("first_name"),
                    "last_name": manager_data.get("last_name"),
                    "department": manager_data.get("department"),
                    "role": manager_data.get("role")
                }
            
            # Include full details or just emails
            if include_details:
                teammates_details = []
                for teammate_email in teammates_emails:
                    teammate = userHelper.get_user_by_email_from_SavingServer(teammate_email)
                    if teammate:
                        teammates_details.append({
                            "id": teammate.ID,
                            "email": teammate.Email,
                            "first_name": teammate.FirstName,
                            "last_name": teammate.LastName,
                            "role": teammate.Role.value if hasattr(teammate.Role, 'value') else teammate.Role,
                            "department": teammate.Department.value if teammate.Department and hasattr(teammate.Department, 'value') else teammate.Department,
                            "address": teammate.Address,
                            "date_of_birth": teammate.DateOfBirth,
                            "employeesList": teammate.EmployeesList
                        })
                result["teammates"] = teammates_details
            else:
                result["teammates"] = teammates_emails
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting teammates: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}"
            }

    @staticmethod
    def get_full_team(employee_email: str) -> Dict[str, Any]:
        """
        Get complete team information including the employee, their manager, and all teammates.
        
        Args:
            employee_email: The email of the employee
            
        Returns:
            Dictionary with full team information
        """
        try:
            # First verify the employee exists
            employee = userHelper.get_user_by_email_from_SavingServer(employee_email)
            if not employee:
                return {
                    "success": False,
                    "error": "Employee not found"
                }
            
            # Find the manager for this employee
            manager_data = userHelper.find_manager_for_employee(employee_email)
            
            if not manager_data:
                # No manager found
                return {
                    "success": True,
                    "employee": {
                        "id": employee.ID,
                        "email": employee.Email,
                        "userID": employee.ID,
                        "first_name": employee.FirstName,
                        "last_name": employee.LastName,
                        "role": employee.Role.value if hasattr(employee.Role, 'value') else employee.Role,
                        "department": employee.Department.value if employee.Department and hasattr(employee.Department, 'value') else employee.Department,
                        "address": employee.Address,
                        "date_of_birth": employee.DateOfBirth,
                        "employeesList": employee.EmployeesList
                    },
                    "message": "No manager found for this employee",
                    "manager": None,
                    "teammates": [],
                    "team_size": 1
                }
            
            # Get all employees under this manager
            employees_list = manager_data.get("employeesList", [])
            
            # Filter out the requesting employee to get only teammates
            teammates_emails = [e for e in employees_list if e.lower() != employee_email.lower()]
            
            # Get full details for all teammates
            teammates_details = []
            for teammate_email in teammates_emails:
                teammate = userHelper.get_user_by_email_from_SavingServer(teammate_email)
                if teammate:
                    teammates_details.append({
                        "id": teammate.ID,
                        "email": teammate.Email,
                        "userID": teammate.ID,
                        "first_name": teammate.FirstName,
                        "last_name": teammate.LastName,
                        "role": teammate.Role.value if hasattr(teammate.Role, 'value') else teammate.Role,
                        "department": teammate.Department.value if teammate.Department and hasattr(teammate.Department, 'value') else teammate.Department
                    })
            
            # Build response
            result = {
                "success": True,
                "employee": {
                    "id": employee.ID,
                    "email": employee.Email,
                    "userID": employee.ID,
                    "first_name": employee.FirstName,
                    "last_name": employee.LastName,
                    "role": employee.Role.value if hasattr(employee.Role, 'value') else employee.Role,
                    "department": employee.Department.value if employee.Department and hasattr(employee.Department, 'value') else employee.Department,
                    "address": employee.Address,
                    "date_of_birth": employee.DateOfBirth,
                    "employeesList": employee.EmployeesList
                },
                "manager": {
                    "email": manager_data.get("email"),
                    "userID": manager_data.get("userID"),
                    "first_name": manager_data.get("first_name"),
                    "last_name": manager_data.get("last_name"),
                    "department": manager_data.get("department"),
                    "role": manager_data.get("role")
                },
                "teammates": teammates_details,
                "team_size": len(teammates_details) + 1  # +1 for the employee themselves
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting full team: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}"
            }