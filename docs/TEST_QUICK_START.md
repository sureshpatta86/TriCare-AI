# Quick Start: Running Tests

This guide will help you quickly set up and run tests for both frontend and backend.

## Backend Tests

### Installation

```bash
cd backend

# Install all dependencies including test packages
pip install -r requirements.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_auth_utils.py

# Run tests matching a pattern
pytest -k "password"

# Run with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run tests and stop on first failure
pytest -x

# Run tests in parallel (faster)
pytest -n auto
```

### View Coverage Report

After running tests with coverage:
```bash
# Open HTML report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Frontend Tests

### Installation

```bash
cd frontend

# Install all dependencies including test packages
npm install
```

### Run Tests

```bash
# Run all tests
npm test

# Run in watch mode (re-runs on file changes)
npm run test:watch

# Run with coverage report
npm run test:coverage

# Run specific test file
npm test -- AuthContext.test.tsx

# Update snapshots
npm test -- -u

# Run tests matching a pattern
npm test -- --testNamePattern="login"
```

### View Coverage Report

After running tests with coverage:
```bash
# Open HTML report in browser
open coverage/lcov-report/index.html  # macOS
xdg-open coverage/lcov-report/index.html  # Linux
start coverage/lcov-report/index.html  # Windows
```

## Common Test Commands

### Backend
```bash
# Quick test run
pytest

# Full coverage analysis
pytest --cov=app --cov-report=html

# Test specific module
pytest tests/test_auth_utils.py -v

# Debug failing test
pytest tests/test_auth_utils.py::TestPasswordHashing::test_hash_password -vv

# Run without warnings
pytest --disable-warnings
```

### Frontend
```bash
# Quick test run
npm test

# Watch mode for development
npm run test:watch

# Coverage report
npm run test:coverage

# Clear cache and run
npm test -- --clearCache && npm test
```

## Test File Locations

### Backend
- **Tests**: `backend/tests/`
- **Configuration**: `backend/pytest.ini`
- **Fixtures**: `backend/tests/conftest.py`
- **Coverage Report**: `backend/htmlcov/`

### Frontend
- **Tests**: `frontend/src/**/__tests__/`
- **Configuration**: `frontend/jest.config.js`
- **Setup**: `frontend/jest.setup.js`
- **Coverage Report**: `frontend/coverage/`

## Expected Test Results

### Backend
```
============================= test session starts ==============================
platform darwin -- Python 3.11.0, pytest-8.2.0
collected 150 items

tests/test_auth_utils.py .........................                       [ 16%]
tests/test_auth_routes.py .............................                 [ 35%]
tests/test_user_model.py ...................                            [ 48%]
tests/test_azure_openai_service.py .......................              [ 63%]
tests/test_doctor_finder_service.py ........................            [ 79%]
tests/test_api_health.py ....                                           [ 82%]
tests/test_imaging_api.py ........                                      [ 87%]
tests/test_reports_api.py ........                                      [ 93%]
tests/test_symptoms_api.py ..........                                   [100%]

============================== 150 passed in 12.45s ============================

---------- coverage: platform darwin, python 3.11.0 -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/utils/auth.py                   95      5    95%
app/models/user.py                  45      2    96%
app/services/azure_openai.py       120     10    92%
app/services/doctor_finder.py      180     15    92%
app/api/routes/auth.py             150     12    92%
-----------------------------------------------------
TOTAL                             1250    105    92%
```

### Frontend
```
PASS  src/contexts/__tests__/AuthContext.test.tsx
PASS  src/lib/__tests__/api-client.test.ts
  
Test Suites: 2 passed, 2 total
Tests:       45 passed, 45 total
Snapshots:   0 total
Time:        3.456 s

----------------------|---------|----------|---------|---------|-------------------
File                  | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s 
----------------------|---------|----------|---------|---------|-------------------
All files             |   88.50 |    85.00 |   92.00 |   89.00 |                   
 contexts             |   95.00 |    90.00 |  100.00 |   95.00 |                   
  AuthContext.tsx     |   95.00 |    90.00 |  100.00 |   95.00 | 45,89            
 lib                  |   92.00 |    88.00 |   95.00 |   93.00 |                   
  api-client.ts       |   92.00 |    88.00 |   95.00 |   93.00 | 78,125,189       
----------------------|---------|----------|---------|---------|-------------------
```

## Troubleshooting

### Backend Issues

**Problem**: Tests fail with import errors
```bash
# Solution: Make sure you're in the backend directory and have the virtual environment activated
cd backend
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Problem**: Database errors during tests
```bash
# Solution: Tests use in-memory SQLite, no setup needed
# If issues persist, try:
pytest --cache-clear
```

**Problem**: Slow tests
```bash
# Solution: Run tests in parallel
pip install pytest-xdist
pytest -n auto
```

### Frontend Issues

**Problem**: Tests fail with module not found
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm test -- --clearCache
```

**Problem**: Tests timeout
```bash
# Solution: Increase timeout in jest.config.js
# Add: testTimeout: 10000
```

**Problem**: Mock issues
```bash
# Solution: Check jest.setup.js and ensure mocks are defined before imports
```

## CI/CD Integration

Tests are automatically run in CI/CD pipelines. Local testing ensures:
- ✅ All tests pass before committing
- ✅ Code coverage meets requirements
- ✅ No breaking changes introduced

### Pre-commit Hook (Optional)

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

echo "Running tests..."

# Backend tests
cd backend
pytest --exitfirst
if [ $? -ne 0 ]; then
    echo "Backend tests failed. Commit aborted."
    exit 1
fi

# Frontend tests
cd ../frontend
npm test -- --watchAll=false
if [ $? -ne 0 ]; then
    echo "Frontend tests failed. Commit aborted."
    exit 1
fi

echo "All tests passed!"
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Writing New Tests

### Backend Template
```python
# tests/test_new_feature.py
import pytest
from app.services.new_service import NewService

class TestNewFeature:
    """Test suite for new feature"""
    
    def test_basic_functionality(self):
        """Test basic case"""
        # Arrange
        service = NewService()
        
        # Act
        result = service.do_something("input")
        
        # Assert
        assert result == "expected"
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test async functionality"""
        service = NewService()
        result = await service.async_method()
        assert result is not None
```

### Frontend Template
```typescript
// src/components/__tests__/NewComponent.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import NewComponent from '../NewComponent'

describe('NewComponent', () => {
  it('should render correctly', () => {
    render(<NewComponent />)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })
  
  it('should handle user interaction', async () => {
    const onClick = jest.fn()
    render(<NewComponent onClick={onClick} />)
    
    await userEvent.click(screen.getByRole('button'))
    
    expect(onClick).toHaveBeenCalled()
  })
})
```

## Getting Help

- **Full Testing Guide**: See [TESTING_GUIDE.md](./TESTING_GUIDE.md)
- **Backend Docs**: Check FastAPI documentation at `/docs` when running server
- **Frontend Docs**: See component documentation in Storybook (if available)

## Summary

**Backend**: `cd backend && pytest --cov=app`
**Frontend**: `cd frontend && npm test`

That's it! You're ready to run tests. For more detailed information, see [TESTING_GUIDE.md](./TESTING_GUIDE.md).
