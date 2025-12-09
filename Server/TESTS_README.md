# Server Tests Documentation

## 📋 Overview

This directory contains comprehensive tests for the Server microservices architecture, including:
- **Tests Unitaires** (Unit Tests)
- **Tests d'Intégration** (Integration/API Tests)  
- **Contract Tests**

## 🗂️ Test Structure

```
Server/
├── tests/
│   ├── __init__.py
│   ├── test_unit.py          # Unit tests for individual components
│   ├── test_integration.py   # Integration tests between services
│   └── test_contract.py      # Contract tests for API specifications
└── Jenkinsfile               # CI/CD pipeline configuration
```

## 🧪 Test Types

### 1. Tests Unitaires (Unit Tests)
**File:** `tests/test_unit.py`

Tests individual functions and modules in isolation:
- ✅ Module imports verification
- ✅ Environment variables validation
- ✅ Service structure verification
- ✅ Role and Department enum tests

**Run:**
```bash
cd Server
python tests/test_unit.py
```

### 2. Tests d'Intégration (Integration Tests)
**File:** `tests/test_integration.py`

Tests interactions between different services:
- ✅ Auth Service health checks
- ✅ Saving Service connectivity
- ✅ Gateway reachability
- ✅ Auth-to-Saving integration flow
- ✅ End-to-end user signup flow

**Run:**
```bash
cd Server
python tests/test_integration.py
```

**Note:** Integration tests require services to be running. Tests will skip gracefully if services are unavailable.

### 3. Contract Tests
**File:** `tests/test_contract.py`

Validates API contracts between services:
- ✅ Auth Service signup/login contracts
- ✅ Saving Service user creation contracts
- ✅ API authentication header contracts
- ✅ Activity creation contracts
- ✅ Cross-service data format consistency
- ✅ User ID, email, and date format validation

**Run:**
```bash
cd Server
python tests/test_contract.py
```

## 🚀 Running All Tests

### Locally
```bash
cd Server

# Install dependencies
pip install pytest requests python-dotenv

# Run all tests
python tests/test_unit.py
python tests/test_integration.py
python tests/test_contract.py
```

### With Jenkins
The `Jenkinsfile` in the Server directory automates all tests:

```groovy
stages:
  1. Checkout
  2. Install Dependencies
  3. Tests Unitaires
  4. Tests d'Intégration (API)
  5. Contract Tests
```

**Setup Jenkins Pipeline:**
1. Create new Pipeline job in Jenkins
2. Point to repository: `https://github.com/yassine4555/5edmet-mas3oud`
3. Set Script Path: `Server/Jenkinsfile`
4. Run the pipeline

## 📊 Test Coverage

### Auth Service
- ✅ User signup contract
- ✅ User login contract
- ✅ Token generation
- ✅ Integration with Saving Service

### Saving Service  
- ✅ User creation endpoint
- ✅ Activity management
- ✅ API authentication
- ✅ Internal API key validation

### Gateway
- ✅ Role enum consistency
- ✅ Department enum consistency
- ✅ Request routing
- ✅ Service orchestration

### Cross-Service
- ✅ User ID format consistency
- ✅ Email format validation
- ✅ Date/datetime format (ISO 8601)
- ✅ API contract compatibility

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the Server directory:

```env
AUTH_SERVER=http://localhost:5000
SAVING_server=http://localhost:5001
GATEWAY_SERVER=http://localhost:8000
INTERNAL_API_KEY=nexus-internal-secret-key-123
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Test Environment
Tests use the following defaults:
- `TESTING=true` - Enables test mode
- `PYTHONPATH=./Server` - Adds Server to Python path

## 📝 Adding New Tests

### Unit Test
```python
class TestNewFeatureUnit(unittest.TestCase):
    def test_new_function(self):
        # Test individual function
        result = my_function()
        self.assertEqual(result, expected_value)
```

### Integration Test
```python
class TestNewServiceIntegration(unittest.TestCase):
    def test_service_communication(self):
        # Test service-to-service communication
        response = requests.get(f"{SERVICE_URL}/endpoint")
        self.assertEqual(response.status_code, 200)
```

### Contract Test
```python
class TestNewAPIContract(unittest.TestCase):
    def test_request_format(self):
        # Validate API request/response format
        expected_fields = ['field1', 'field2']
        sample_request = {"field1": "value", "field2": "value"}
        for field in expected_fields:
            self.assertIn(field, sample_request)
```

## ✅ Success Criteria

All tests pass when:
- ✅ All imports succeed
- ✅ Environment variables are configured
- ✅ API contracts match between services
- ✅ Data formats are consistent
- ✅ Services can communicate (when running)

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure PYTHONPATH includes Server directory
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Missing Dependencies
```bash
pip install -r authService/requirements.txt
pip install -r Gateway/requirements.txt
pip install pytest requests python-dotenv
```

### Integration Tests Skipping
- This is normal if services aren't running
- Start services individually to run full integration tests

## 📚 Related Documentation

- `DataBase2/verify_api.py` - Database API tests
- `DataBase2/verify_models.py` - Database model tests
- `SERVER_TEAM_INTEGRATION_GUIDE.md` - Service integration guide
- `GATEWAY_API_DOCUMENTATION.md` - Gateway API documentation

---

**Created:** December 8, 2025  
**Purpose:** Jenkins CI/CD pipeline testing for Server microservices
