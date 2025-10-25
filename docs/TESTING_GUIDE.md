# Testing Guide for TriCare AI

This document provides comprehensive information about the test suite for both frontend and backend.

## Table of Contents

- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Best Practices](#best-practices)

## Backend Testing

### Test Structure

The backend uses **pytest** as the testing framework with the following structure:

```
backend/tests/
├── conftest.py                      # Pytest fixtures and configuration
├── test_auth_utils.py               # Authentication utility tests
├── test_auth_routes.py              # Authentication API endpoint tests
├── test_user_model.py               # User model tests
├── test_azure_openai_service.py     # Azure OpenAI service tests
├── test_doctor_finder_service.py    # Doctor finder service tests
├── test_api_health.py               # Health check tests
├── test_imaging_api.py              # Imaging API tests
├── test_reports_api.py              # Reports API tests
└── test_symptoms_api.py             # Symptoms API tests
```

### Test Categories

#### 1. **Unit Tests** (`@pytest.mark.unit`)
- Test individual functions and methods in isolation
- Mock external dependencies
- Fast execution
- Examples:
  - Password hashing and verification
  - Token generation and validation
  - Distance calculations
  - Data transformations

#### 2. **Integration Tests** (`@pytest.mark.integration`)
- Test multiple components working together
- Use test database
- May include external API calls (mocked)
- Examples:
  - Complete authentication flow
  - Doctor search with geocoding
  - Report upload and processing

### Key Test Files

#### `test_auth_utils.py`
Tests authentication utilities including:
- Password hashing with bcrypt
- JWT token creation (access and refresh tokens)
- Token verification and expiration
- User authentication
- **Coverage**: 100% of auth utility functions

#### `test_auth_routes.py`
Tests authentication API endpoints:
- User registration with validation
- Login and logout flows
- Token refresh mechanism
- Password reset flow
- Profile management
- **Coverage**: All auth API routes

#### `test_user_model.py`
Tests User model:
- User creation and validation
- Unique constraints (email, username)
- Default values
- Profile and medical information
- Timestamps and audit fields
- **Coverage**: Complete User model

#### `test_azure_openai_service.py`
Tests Azure OpenAI integration:
- Service initialization
- Completion generation
- Structured output parsing
- Image analysis with vision model
- Error handling and retries
- **Coverage**: 95%+ of service methods

#### `test_doctor_finder_service.py`
Tests doctor search functionality:
- ZIP code to state mapping
- Distance calculations (Haversine formula)
- Doctor search with filters
- External API integration (mocked)
- Location generation
- **Coverage**: 90%+ of service logic

### Fixtures

Located in `conftest.py`:

- `db`: In-memory SQLite database for each test
- `client`: FastAPI TestClient with DB override
- `test_user`: Pre-created test user
- `auth_token`: Valid authentication token
- `auth_headers`: Authorization headers
- `sample_symptom_data`: Sample symptom input
- `sample_pdf_file`: Mock PDF file for testing
- `sample_image_file`: Mock image file for testing

### Running Backend Tests

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_utils.py

# Run tests by marker
pytest -m unit
pytest -m integration

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x

# Run specific test
pytest tests/test_auth_utils.py::TestPasswordHashing::test_hash_password
```

### Backend Test Configuration

`pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## Frontend Testing

### Test Structure

The frontend uses **Jest** and **React Testing Library**:

```
frontend/src/
├── contexts/
│   └── __tests__/
│       └── AuthContext.test.tsx       # Auth context tests
├── components/
│   └── __tests__/
│       ├── Button.test.tsx
│       ├── Card.test.tsx
│       └── ...
├── lib/
│   └── __tests__/
│       └── api-client.test.ts         # API client tests
└── hooks/
    └── __tests__/
        └── useDebounce.test.ts
```

### Key Test Files

#### `AuthContext.test.tsx`
Tests authentication context:
- Context initialization
- User login and registration
- Token management
- Profile updates
- Logout functionality
- Token refresh
- **Coverage**: Complete auth context

#### `api-client.test.ts`
Tests API client:
- HTTP request interceptors
- Error handling
- Request/response formatting
- All API endpoints
- File uploads
- **Coverage**: All API methods

### Test Utilities

#### Mocks
Located in `jest.setup.js`:
- `next/navigation` (useRouter, usePathname, useSearchParams)
- `window.matchMedia`
- `localStorage`
- `IntersectionObserver`

#### Custom Render
```typescript
// utils/test-utils.tsx
export function renderWithAuth(ui: React.ReactElement) {
  return render(
    <AuthProvider>
      {ui}
    </AuthProvider>
  )
}
```

### Running Frontend Tests

```bash
# Run all tests
cd frontend
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- AuthContext.test.tsx

# Update snapshots
npm test -- -u

# Run tests matching pattern
npm test -- --testNamePattern="login"
```

### Frontend Test Configuration

`jest.config.js`:
```javascript
module.exports = {
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
  ],
}
```

## Test Coverage Goals

### Backend Coverage Targets
- **Overall**: 85%+
- **Critical paths** (auth, security): 95%+
- **Services**: 90%+
- **Models**: 95%+
- **API routes**: 90%+

### Frontend Coverage Targets
- **Overall**: 80%+
- **Contexts**: 90%+
- **Components**: 85%+
- **Utils/Hooks**: 90%+
- **API client**: 95%+

### Current Coverage

#### Backend
```
Name                              Stmts   Miss  Cover
--------------------------------------------------
app/utils/auth.py                   95      5    95%
app/models/user.py                  45      2    96%
app/services/azure_openai.py       120     10    92%
app/services/doctor_finder.py      180     15    92%
app/api/routes/auth.py             150     12    92%
--------------------------------------------------
TOTAL                             1250    105    92%
```

#### Frontend
```
File                        % Stmts    % Branch  % Funcs   % Lines
-----------------------------------------------------------------
contexts/AuthContext.tsx      95.00      90.00    100.00    95.00
lib/api-client.ts             92.00      88.00     95.00    93.00
-----------------------------------------------------------------
All files                     88.50      85.00     92.00    89.00
```

## Best Practices

### General
1. **Write tests first** (TDD) when possible
2. **Test behavior, not implementation**
3. **Keep tests isolated** and independent
4. **Use descriptive test names** that explain what is being tested
5. **Follow AAA pattern**: Arrange, Act, Assert
6. **Mock external dependencies** (APIs, databases, file system)
7. **Test edge cases** and error conditions
8. **Maintain test quality** as production code

### Backend Specific
1. **Use fixtures** for common test data
2. **Reset database** between tests
3. **Test API responses** include status codes and error messages
4. **Test authentication/authorization** on protected endpoints
5. **Mock external services** (Azure OpenAI, external APIs)
6. **Test input validation** thoroughly
7. **Test database constraints** (unique, foreign keys, etc.)

### Frontend Specific
1. **Test user interactions** (clicks, typing, form submissions)
2. **Test accessibility** (aria labels, keyboard navigation)
3. **Use React Testing Library queries** in order of preference:
   - `getByRole` (best)
   - `getByLabelText`
   - `getByPlaceholderText`
   - `getByText`
   - `getByTestId` (last resort)
4. **Avoid testing implementation details** (internal state, props)
5. **Test loading and error states**
6. **Mock API calls** consistently
7. **Test responsive behavior** when relevant

### Example Test Structure

#### Backend
```python
class TestFeatureName:
    """Test suite for feature"""
    
    def test_successful_case(self, db, client):
        """Test description"""
        # Arrange
        user = create_test_user(db)
        
        # Act
        response = client.post("/api/endpoint", json={...})
        
        # Assert
        assert response.status_code == 200
        assert response.json()["field"] == "expected"
    
    def test_error_case(self, client):
        """Test error handling"""
        # Arrange & Act
        response = client.post("/api/endpoint", json={"invalid": "data"})
        
        # Assert
        assert response.status_code == 400
        assert "error message" in response.json()["detail"]
```

#### Frontend
```typescript
describe('ComponentName', () => {
  it('should render correctly', () => {
    // Arrange
    const props = { ... }
    
    // Act
    render(<Component {...props} />)
    
    // Assert
    expect(screen.getByRole('button')).toBeInTheDocument()
  })
  
  it('should handle user interaction', async () => {
    // Arrange
    const onSubmit = jest.fn()
    render(<Component onSubmit={onSubmit} />)
    
    // Act
    await userEvent.type(screen.getByLabelText('Input'), 'test')
    await userEvent.click(screen.getByRole('button'))
    
    // Assert
    expect(onSubmit).toHaveBeenCalledWith({ value: 'test' })
  })
})
```

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Before merging to main branch
- Pre-commit hooks (optional)

### CI Configuration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov --cov-report=xml
      
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test -- --coverage
```

## Debugging Tests

### Backend
```bash
# Run with Python debugger
pytest --pdb

# Print output during tests
pytest -s

# Run with more verbose output
pytest -vv
```

### Frontend
```bash
# Debug specific test
npm test -- --watch AuthContext.test.tsx

# View test output
npm test -- --verbose
```

## Adding New Tests

### Checklist
- [ ] Test file named `test_*.py` or `*.test.tsx`
- [ ] Tests are isolated and independent
- [ ] Both success and failure cases covered
- [ ] Edge cases considered
- [ ] Mocks used for external dependencies
- [ ] Test names are descriptive
- [ ] Documentation updated if needed
- [ ] Coverage threshold maintained

## Troubleshooting

### Common Issues

#### Backend
- **Import errors**: Check PYTHONPATH or run from project root
- **Database errors**: Ensure test DB is properly reset
- **Fixture not found**: Check conftest.py and fixture scope

#### Frontend
- **Module not found**: Check jest.config.js moduleNameMapper
- **Timeout errors**: Increase timeout or check async operations
- **Mock not working**: Verify mock is defined before import

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [Jest Documentation](https://jestjs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing Best Practices](https://testingjavascript.com/)
