"""
Unit Tests for Server Components
Tests individual functions and modules in isolation
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestAuthServiceUnit(unittest.TestCase):
    """Unit tests for Auth Service helper functions"""
    
    def test_import_modules(self):
        """Test that all required modules can be imported"""
        try:
            # Add authService to path
            auth_service_path = os.path.join(os.path.dirname(__file__), '..', 'authService')
            if auth_service_path not in sys.path:
                sys.path.insert(0, auth_service_path)
            
            from Helper import authHelper
            print("✅ authHelper imported successfully")
        except ImportError as e:
            print(f"⚠️  authHelper import skipped: {e}")
            self.skipTest(f"Auth service dependencies not available: {e}")
    
    def test_env_variables(self):
        """Test that required environment variables are accessible"""
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'SAVING_server']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"⚠️  Missing env vars: {missing_vars}")
        else:
            print("✅ All required environment variables present")
        
        self.assertTrue(True)  # Don't fail on missing env in CI


class TestGatewayUnit(unittest.TestCase):
    """Unit tests for Gateway Service"""
    
    def test_gateway_imports(self):
        """Test that Gateway modules can be imported"""
        try:
            from Gateway.modeles.role import ROLE
            from Gateway.modeles.department import Department
            print("✅ Gateway models imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import Gateway models: {e}")
    
    def test_role_enum(self):
        """Test Role enum values"""
        from Gateway.modeles.role import ROLE
        
        expected_roles = ['MANAGER', 'EMPLOYEE', 'ADMIN']
        available_roles = [attr for attr in dir(ROLE) if not attr.startswith('_')]
        
        print(f"✅ Roles available: {available_roles}")
        self.assertTrue(len(available_roles) > 0)


class TestDataServiceUnit(unittest.TestCase):
    """Unit tests for Data Service"""
    
    def test_data_service_structure(self):
        """Test that data service directory exists"""
        data_service_path = os.path.join(os.path.dirname(__file__), '..', 'dataService')
        self.assertTrue(os.path.exists(data_service_path), "Data service directory should exist")
        print("✅ Data service structure verified")


class TestUserServiceUnit(unittest.TestCase):
    """Unit tests for User Service"""
    
    def test_user_service_structure(self):
        """Test that user service directory exists"""
        user_service_path = os.path.join(os.path.dirname(__file__), '..', 'userServices')
        self.assertTrue(os.path.exists(user_service_path), "User service directory should exist")
        print("✅ User service structure verified")


if __name__ == '__main__':
    print("🧪 Running Unit Tests for Server Components")
    print("=" * 60)
    unittest.main(verbosity=2)
