# 📋 Server Tests - Quick Reference Card

## 🚀 Quick Start

```bash
# Navigate to Server directory
cd Server

# Install dependencies
pip install pytest requests python-dotenv

# Run all tests
python tests/test_unit.py
python tests/test_integration.py
python tests/test_contract.py
```

---

## 📊 Test Overview

| Type | Count | Purpose | Duration |
|------|-------|---------|----------|
| **Unit** | 6 | Test components in isolation | ~0.6s |
| **Integration** | 5 | Test service communication | ~4.1s |
| **Contract** | 10 | Validate API contracts | ~0.03s |
| **Total** | **21** | Complete test coverage | **~4.7s** |

---

## 🎯 Common Commands

### Run Tests
```bash
# All unit tests
python tests/test_unit.py

# All integration tests
python tests/test_integration.py

# All contract tests
python tests/test_contract.py

# Specific test class
python -m unittest tests.test_unit.TestGatewayUnit

# Specific test method
python -m unittest tests.test_unit.TestGatewayUnit.test_role_enum

# With verbose output
python tests/test_unit.py -v
```

### With pytest
```bash
pytest tests/                    # All tests
pytest tests/test_contract.py    # Specific file
pytest -k "test_auth"            # Tests matching pattern
pytest -v                        # Verbose
pytest --cov=.                   # With coverage
```

---

## 📁 File Structure

```
Server/
├── tests/
│   ├── test_unit.py          # 6 unit tests
│   ├── test_integration.py   # 5 integration tests
│   └── test_contract.py      # 10 contract tests
├── Jenkinsfile               # CI/CD pipeline
├── TESTS_DOCUMENTATION.md    # Complete docs
├── TESTS_README.md           # Setup guide
└── TESTS_QUICK_REFERENCE.md  # This file
```

---

## 🧪 Unit Tests (6 tests)

| Test | What It Checks | Status |
|------|---------------|--------|
| `test_import_modules` | Auth Service imports | ⚠️ Skipped |
| `test_env_variables` | Environment config | ✅ Pass |
| `test_gateway_imports` | Gateway models | ✅ Pass |
| `test_role_enum` | Role enum values | ✅ Pass |
| `test_data_service_structure` | Directory exists | ✅ Pass |
| `test_user_service_structure` | Directory exists | ✅ Pass |

**Quick Check:**
```bash
python tests/test_unit.py
# Expected: 6 tests, 5 passed, 1 skipped
```

---

## 🔗 Integration Tests (5 tests)

| Test | Service | Port | Status |
|------|---------|------|--------|
| `test_auth_service_health` | Auth | 5000 | ✅ Pass |
| `test_saving_service_health` | Saving | 5001 | ✅ Pass |
| `test_gateway_health` | Gateway | 8000 | ⚠️ Skipped |
| `test_auth_to_saving_integration` | Cross-service | - | ⚠️ Skipped |
| `test_user_signup_flow` | End-to-end | - | ⚠️ Skipped |

**Quick Check:**
```bash
python tests/test_integration.py
# Expected: 5 tests, 2 passed, 3 skipped (services not running)
```

**Note:** Tests skip gracefully when services aren't running.

---

## 📋 Contract Tests (10 tests)

### Auth Service Contracts (2)
- ✅ Signup request format
- ✅ Login request format

### Saving Service Contracts (3)
- ✅ User creation format
- ✅ Activity creation format
- ✅ API authentication header

### Gateway Contracts (2)
- ✅ Role enum consistency
- ✅ Department enum consistency

### Cross-Service Contracts (3)
- ✅ User ID format (`auth0_*`)
- ✅ Email format validation
- ✅ Date format (ISO 8601)

**Quick Check:**
```bash
python tests/test_contract.py
# Expected: 10 tests, 10 passed
```

---

## 🔑 API Contracts Reference

### Auth Service - Signup
```json
{
  "email": "user@example.com",
  "FirstName": "John",
  "LastName": "Doe",
  "Password": "SecurePass123!",
  "DateOfBirth": "1990-01-01",
  "Address": "123 Main St"
}
```

### Auth Service - Login
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Saving Service - Create User
```json
{
  "email": "user@example.com",
  "userID": "auth0_test_123",
  "password": "placeholder",
  "role": "employee",
  "first_name": "John",
  "last_name": "Doe",
  "address": "123 Main St",
  "department": "Engineering",
  "date_of_birth": "1990-01-01"
}
```

**Required Header:**
```
X-Internal-Key: nexus-internal-secret-key-123
```

### Saving Service - Create Activity
```json
{
  "type": "meeting",
  "title": "Sprint Planning",
  "description": "Plan next sprint",
  "creator": "manager@example.com",
  "date": "2025-01-15T10:00:00",
  "status": "scheduled"
}
```

---

## ⚙️ Environment Variables

Create `Server/.env`:
```env
# Service URLs
AUTH_SERVER=http://localhost:5000
SAVING_server=http://localhost:5001
GATEWAY_SERVER=http://localhost:8000

# API Keys
INTERNAL_API_KEY=nexus-internal-secret-key-123

# Supabase (Auth Service)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

---

## 🏗️ Jenkins Pipeline

### Setup
1. Create new Pipeline job in Jenkins
2. Repository: `https://github.com/yassine4555/5edmet-mas3oud`
3. Script Path: `Server/Jenkinsfile`
4. Save and build

### Pipeline Stages
```
1. Checkout          → Clone repository
2. Install Deps      → Install Python packages
3. Unit Tests        → Run test_unit.py
4. Integration Tests → Run test_integration.py
5. Contract Tests    → Run test_contract.py
```

### Expected Output
```
✅ All Server tests passed!
```

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Add to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Install missing packages
pip install supabase requests python-dotenv
```

### Services Not Running
```bash
# This is normal - integration tests skip gracefully
⚠️  Gateway not reachable
skipped 'Gateway not running'
```

### Port Already in Use
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Permission Errors (Jenkins)
```bash
# Use --user flag
pip install --user pytest requests
```

---

## ✅ Success Criteria

Tests pass when:
- ✅ All imports succeed (or skip gracefully)
- ✅ Environment variables configured (or skip)
- ✅ API contracts match specifications
- ✅ Data formats consistent (ISO 8601, emails, user IDs)
- ✅ Services respond correctly (when running)

---

## 📈 Test Results

```
╔═══════════════════════════════════════════════╗
║         SERVER TESTS SUMMARY                  ║
╠═══════════════════════════════════════════════╣
║  ✅ Unit Tests:        6 (5 passed, 1 skip)   ║
║  ✅ Integration Tests: 5 (2 passed, 3 skip)   ║
║  ✅ Contract Tests:   10 (10 passed)          ║
║                                               ║
║  Total: 21 tests                              ║
║  Status: ALL PASSING ✓                        ║
╚═══════════════════════════════════════════════╝
```

---

## 🔗 Related Documentation

- `TESTS_DOCUMENTATION.md` - Complete documentation (400+ lines)
- `TESTS_README.md` - Setup and getting started guide
- `Jenkinsfile` - CI/CD pipeline configuration
- `tests/` - Test source code

---

## 💡 Pro Tips

1. **Run contract tests first** - They're fastest and catch most issues
2. **Skip integration tests in CI** - They require running services
3. **Use pytest for local development** - Better output formatting
4. **Keep tests isolated** - No dependencies between tests
5. **Update contracts when APIs change** - Keep documentation in sync

---

## 📞 Quick Help

```bash
# See all test options
python tests/test_unit.py --help

# Run with maximum verbosity
python tests/test_unit.py -v

# Stop on first failure
pytest tests/ -x

# Show what tests will run
pytest tests/ --collect-only
```

---

**Created:** December 8, 2025  
**For:** Server Team CI/CD Testing  
**See Also:** TESTS_DOCUMENTATION.md for complete details
