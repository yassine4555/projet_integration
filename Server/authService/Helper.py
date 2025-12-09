from supaBase.supaBase import dataBaseAuth
import json
import os
import requests

from dotenv import load_dotenv

class authHelper : 
    
    def __init__(self,database : dataBaseAuth):
        load_dotenv()
        self.userService = os.getenv("userService")
        self.authenticater=database
    
    def CreateUser(self,Email,password):
        try:
            print("result : ")
            result = self.authenticater.createUser(Email,password)
            print("result type : ", type(result))
            if(result is not None):
                result = json.loads(result)
                session = (result.get("session", {}))
                user = (result.get("user", {}))
                print("user : ")
                print(user)
                print("seesion : ")
                print(session)
                return json.dumps({"Token":session.get("access_token"),"id":user.get("id")})
        except Exception as e:
            print(f"Auth creation error: {e}")
            return None
        
    
    def login (self,Email,password):
        try:
            print("email : ",Email)
            print("passwor : " , password)
            result = self.authenticater.login(Email,password)
            print("result type : ", type(result))
            if(result is not None):
                result = json.loads(result)
                session = (result.get("session", {}))
                user = (result.get("user", {}))
                print("user : ")
                print(user)
                print("seesion : ")
                print(session)
                
                # FIX: Get the response and parse it as JSON
                userFromServiceResponse = requests.get(f'http://{self.userService}/users/by-email/{Email}')
                
                # Check if request was successful
                if userFromServiceResponse.status_code == 200:
                    userFromService = userFromServiceResponse.json()
                else:
                    print(f"Failed to get user from service: {userFromServiceResponse.status_code}")
                    userFromService = {}

                return json.dumps({
                    "Token": session.get("access_token"),
                    "id": user.get("id"),
                    "firstname": userFromService.get("FirstName", ""),
                    "lastname": userFromService.get("LastName", ""),
                    "role": userFromService.get("Role", "")
                })
            else:
                # FIX: Return None instead of False so json.loads() doesn't fail
                return None
        except Exception as e:
            print(f"Auth login error: {e}")
            # FIX: Return None instead of False
            return None
        
    def deleteUser(self,userId):
        try:
            result = self.authenticater.delUser(userId)
            if(result is not None):
                result = json.loads(result)
                print(result)
                return json.dumps({"status":"user deleted"})
        except Exception as e :
            print(f"matna7ach user :{userId} ")
    
    def getUserEmailById(self, userId):
        """Get user email by user ID"""
        try:
            result = self.authenticater.getUserById(userId)
            if result is not None:
                result = json.loads(result)
                user = result.get("user", {})
                email = user.get("email")
                if email:
                    return json.dumps({"email": email, "id": userId})
                else:
                    return None
        except Exception as e:
            print(f"Error getting user email for userId {userId}: {e}")
            return None