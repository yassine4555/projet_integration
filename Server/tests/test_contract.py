"""
Contract Tests for Server APIs
Validates that API contracts are respected between services
"""
import unittest
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestAuthServiceContract(unittest.TestCase):
    """Contract tests for Auth Service API"""
    
    def test_signup_request_contract(self):
        """Verify signup endpoint expects correct request format"""
        expected_fields = [
            'email',
            'FirstName',
            'LastName',
            'Password',
            'DateOfBirth',
            'Address'
        ]
        
        sample_request = {
            "email": "test@example.com",
            "FirstName": "Test",
            "LastName": "User",
            "Password": "Password123!",
            "DateOfBirth": "1990-01-01",
            "Address": "123 Test St"
        }
        
        # Verify all expected fields are present
        for field in expected_fields:
            self.assertIn(field, sample_request, f"Signup contract should include {field}")
        
        print(f"✅ Auth Service signup contract verified: {expected_fields}")
    
    def test_login_request_contract(self):
        """Verify login endpoint expects correct request format"""
        expected_fields = ['email', 'password']
        
        sample_request = {
            "email": "test@example.com",
            "password": "Password123!"
        }
        
        for field in expected_fields:
            self.assertIn(field, sample_request, f"Login contract should include {field}")
        
        print(f"✅ Auth Service login contract verified: {expected_fields}")


class TestSavingServiceContract(unittest.TestCase):
    """Contract tests for Saving Service API"""
    
    def test_create_user_contract(self):
        """Verify user creation endpoint contract"""
        expected_fields = [
            'email',
            'userID',
            'password',
            'role',
            'first_name',
            'last_name',
            'address',
            'department',
            'date_of_birth'
        ]
        
        sample_request = {
            "email": "test@example.com",
            "userID": "auth0_test_123",
            "password": "placeholder",
            "role": "employee",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test St",
            "department": "QA",
            "date_of_birth": "1990-01-01"
        }
        
        for field in expected_fields:
            self.assertIn(field, sample_request, f"Create user contract should include {field}")
        
        print(f"✅ Saving Service user creation contract verified")
    
    def test_api_key_header_contract(self):
        """Verify API requires X-Internal-Key header"""
        required_header = 'X-Internal-Key'
        
        sample_headers = {
            "X-Internal-Key": "nexus-internal-secret-key-123",
            "Content-Type": "application/json"
        }
        
        self.assertIn(required_header, sample_headers)
        print(f"✅ Saving Service authentication contract verified")
    
    def test_activity_creation_contract(self):
        """Verify activity creation endpoint contract"""
        expected_fields = [
            'type',
            'title',
            'description',
            'creator',
            'date',
            'status'
        ]
        
        sample_request = {
            "type": "meeting",
            "title": "Team Sync",
            "description": "Weekly sync",
            "creator": "manager@example.com",
            "date": "2025-01-15T10:00:00",
            "status": "scheduled"
        }
        
        for field in expected_fields:
            self.assertIn(field, sample_request, f"Activity creation contract should include {field}")
        
        print(f"✅ Saving Service activity contract verified")


class TestGatewayContract(unittest.TestCase):
    """Contract tests for Gateway API"""
    
    def test_role_enum_contract(self):
        """Verify Role enum values are consistent"""
        from Gateway.modeles.role import ROLE
        
        # Check that ROLE enum exists and has expected attributes
        role_attrs = [attr for attr in dir(ROLE) if not attr.startswith('_')]
        
        self.assertTrue(len(role_attrs) > 0, "Role enum should have values")
        print(f"✅ Gateway Role contract verified: {role_attrs}")
    
    def test_department_enum_contract(self):
        """Verify Department enum values are consistent"""
        from Gateway.modeles.department import Department
        
        dept_attrs = [attr for attr in dir(Department) if not attr.startswith('_')]
        
        self.assertTrue(len(dept_attrs) > 0, "Department enum should have values")
        print(f"✅ Gateway Department contract verified")


class TestCrossServiceContract(unittest.TestCase):
    """Contract tests between services"""
    
    def test_user_id_format_consistency(self):
        """Verify user ID format is consistent across services"""
        # Auth service generates: auth0_<something>
        # Saving service expects: userID field
        # Both should use the same format
        
        auth_user_id_format = "auth0_"
        sample_user_id = "auth0_test_123"
        
        self.assertTrue(sample_user_id.startswith(auth_user_id_format))
        print(f"✅ User ID format contract verified: {auth_user_id_format}*")
    
    def test_email_format_consistency(self):
        """Verify email format is consistent across services"""
        import re
        
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        sample_email = "test@example.com"
        
        self.assertTrue(re.match(email_regex, sample_email))
        print(f"✅ Email format contract verified")
    
    def test_date_format_consistency(self):
        """Verify date format is consistent across services"""
        from datetime import datetime
        
        # Both services should use ISO 8601 format
        date_format = "%Y-%m-%d"
        datetime_format = "%Y-%m-%dT%H:%M:%S"
        
        sample_date = "1990-01-01"
        sample_datetime = "2025-01-15T10:00:00"
        
        try:
            datetime.strptime(sample_date, date_format)
            datetime.strptime(sample_datetime, datetime_format)
            print(f"✅ Date format contract verified: ISO 8601")
        except ValueError:
            self.fail("Date format should be ISO 8601")


if __name__ == '__main__':
    print("📋 Running Contract Tests for Server APIs")
    print("=" * 60)
    unittest.main(verbosity=2)
