import os
from supabase import create_client, Client, ClientOptions
import httpx
import logging

logger = logging.getLogger(__name__)

class dataBaseAuth:
    def __init__(self, url, key):
        # Increase timeout and add retry logic
        timeout = httpx.Timeout(120.0, connect=30.0)
        http_client = httpx.Client(
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            follow_redirects=True
        )
        options = ClientOptions({
            'auth': {'http_client': http_client}
        })
        self.supabase: Client = create_client(url, key, options)

    def createUser(self, email, password):
        """Create a new user in Supabase Auth"""
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            return response.model_dump_json()
        except httpx.RemoteProtocolError as e:
            logger.error(f"Supabase connection error during sign_up: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def login(self, email, password):
        """Sign in user with email and password"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            return response.model_dump_json()
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return None

    def delUser(self, userId):
        """Delete user by ID (admin operation)"""
        try:
            response = self.supabase.auth.admin.delete_user(userId)
            return response.model_dump_json()
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return None

    def getUserById(self, userId):
        """Get user information by user ID from Supabase Auth (admin operation)"""
        try:
            response = self.supabase.auth.admin.get_user_by_id(userId)
            return response.model_dump_json()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

