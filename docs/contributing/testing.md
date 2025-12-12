# Testing Guide

Testing guidelines for ChatOps.

## Backend Tests

### Running Tests

```bash
cd api
pytest
```

### Test Structure

- `tests/` - Test files
- `conftest.py` - Pytest configuration and fixtures
- `test_*.py` - Test modules

### Writing Tests

```python
def test_example(client: TestClient):
    """Test example endpoint."""
    response = client.get("/api/v1/example")
    assert response.status_code == 200
```

## Frontend Tests

### Running Tests

```bash
cd web
npm test
```

## Test Coverage

- Aim for >80% coverage
- Test critical paths
- Test error cases
- Test edge cases

## Next Steps

- [Development Setup](development.md)

