# Testing Documentation
## Translation Chain Vector Distance Analysis

**Version:** 1.0  
**Date:** November 18, 2025

---

## Table of Contents
1. [Testing Strategy](#testing-strategy)
2. [Test Coverage](#test-coverage)
3. [Edge Cases](#edge-cases)
4. [Running Tests](#running-tests)
5. [CI/CD Integration](#cicd-integration)

---

## 1. Testing Strategy

### 1.1 Testing Approach

We employ a comprehensive testing strategy targeting **85%+ code coverage** using pytest framework:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Mock Testing**: External dependency simulation
- **Edge Case Testing**: Boundary conditions and error scenarios

### 1.2 Test Organization

```
tests/
├── test_agents.py         # Agent implementations
├── test_translation.py    # Translation chain & error injection
├── test_analysis.py       # Embeddings, distance, statistics
├── test_data.py           # Data generation & storage
└── test_config.py         # Configuration management
```

---

## 2. Test Coverage

### 2.1 Coverage Targets

| Component | Target Coverage | Priority |
|-----------|----------------|----------|
| Agents | ≥85% | Critical |
| Translation Chain | ≥85% | Critical |
| Error Injection | ≥90% | High |
| Embeddings | ≥80% | High |
| Distance Metrics | ≥90% | High |
| Statistics | ≥85% | High |
| Data Storage | ≥85% | High |
| Configuration | ≥75% | Medium |
| Visualization | ≥70% | Medium |

### 2.2 Current Coverage

Run tests with coverage reporting:

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

View HTML report:
```bash
open results/coverage/html/index.html
```

---

## 3. Edge Cases

### 3.1 Agent Layer

#### Test Case: Empty Input
- **Scenario**: Agent receives empty string
- **Expected**: `ValueError` raised with message "Text cannot be empty"
- **Test**: `test_validate_input_empty_text()`

#### Test Case: Invalid Language Code
- **Scenario**: Agent receives unsupported language
- **Expected**: `ValueError` raised with message "Invalid source language"
- **Test**: `test_validate_input_invalid_source_lang()`

#### Test Case: Same Source and Target Language
- **Scenario**: User requests translation from English to English
- **Expected**: `ValueError` raised
- **Test**: `test_validate_input_same_languages()`

#### Test Case: Command Not Found
- **Scenario**: CLI tool not installed or not in PATH
- **Expected**: `RuntimeError` with helpful installation message
- **Test**: `test_translate_command_not_found()`
- **Recovery**: Inform user to install the CLI tool

#### Test Case: Translation Timeout
- **Scenario**: Translation takes longer than configured timeout
- **Expected**: Retry logic attempts up to 3 times, then fails with timeout error
- **Test**: `test_translate_timeout()`
- **Recovery**: Increase timeout in configuration

#### Test Case: Empty Translation Output
- **Scenario**: Agent returns empty string
- **Expected**: `RuntimeError` raised
- **Test**: `test_translate_empty_output()`
- **Recovery**: Retry with different prompt formulation

### 3.2 Error Injection Layer

#### Test Case: Zero Error Rate
- **Scenario**: Error rate = 0.0
- **Expected**: Text returned unchanged
- **Test**: `test_inject_errors_zero_rate()`

#### Test Case: Maximum Error Rate
- **Scenario**: Error rate = 1.0 (100%)
- **Expected**: All words corrupted, word count preserved
- **Test**: Implementation validates 0.0 ≤ error_rate ≤ 1.0

#### Test Case: Error Rate Out of Bounds
- **Scenario**: Error rate < 0 or > 1
- **Expected**: `ValueError` raised
- **Test**: `test_inject_errors_invalid_rate()`

#### Test Case: Single Word Sentence
- **Scenario**: Sentence with only 1 word
- **Expected**: Either corrupted or unchanged, no crash
- **Test**: Boundary condition tested

#### Test Case: Punctuation Preservation
- **Scenario**: Sentence with complex punctuation
- **Expected**: Punctuation marks preserved in output
- **Test**: `test_maintain_punctuation()`

#### Test Case: Unicode Characters
- **Scenario**: Text containing non-ASCII characters (é, ñ, ü, etc.)
- **Expected**: Correct handling without encoding errors
- **Test**: Manual verification required

### 3.3 Translation Chain Layer

#### Test Case: Chain Failure Mid-Execution
- **Scenario**: Second translation step fails
- **Expected**: `ChainResult` with success=False, partial translations stored
- **Test**: `test_execute_chain_failure()`
- **Recovery**: Results still stored for analysis

#### Test Case: Very Long Sentence
- **Scenario**: Sentence with >100 words
- **Expected**: Successful processing without truncation
- **Test**: Manual testing with long inputs

#### Test Case: Special Characters in Text
- **Scenario**: Text with emojis, symbols, newlines
- **Expected**: Proper handling or graceful degradation
- **Test**: Manual verification required

### 3.4 Vector Analysis Layer

#### Test Case: Identical Vectors
- **Scenario**: Computing distance between identical embeddings
- **Expected**: Cosine distance ≈ 0
- **Test**: `test_cosine_distance_identical()`

#### Test Case: Opposite Vectors
- **Scenario**: Vectors pointing in opposite directions
- **Expected**: Cosine distance ≈ 2.0
- **Test**: `test_cosine_distance_opposite()`

#### Test Case: Orthogonal Vectors
- **Scenario**: Perpendicular vectors
- **Expected**: Cosine distance ≈ 1.0
- **Test**: `test_cosine_distance_orthogonal()`

#### Test Case: Shape Mismatch
- **Scenario**: Comparing vectors of different dimensions
- **Expected**: `ValueError` raised
- **Test**: `test_distance_shape_mismatch()`

#### Test Case: NaN or Inf in Embeddings
- **Scenario**: Corrupted embedding with invalid values
- **Expected**: Proper error handling or filtering
- **Test**: Additional validation needed

### 3.5 Data Storage Layer

#### Test Case: Database File Not Writable
- **Scenario**: No write permissions for database directory
- **Expected**: Clear error message during initialization
- **Test**: Manual verification required

#### Test Case: Concurrent Database Access
- **Scenario**: Multiple processes writing simultaneously
- **Expected**: SQLite handles with WAL mode enabled
- **Test**: Performance testing required

#### Test Case: Disk Space Exhausted
- **Scenario**: No space left on device
- **Expected**: Graceful error with helpful message
- **Test**: Manual verification required

#### Test Case: Duplicate Sentence Storage
- **Scenario**: Same sentence stored multiple times
- **Expected**: `get_or_create_sentence()` returns existing ID
- **Test**: `test_get_or_create_sentence_existing()`

### 3.6 Configuration Layer

#### Test Case: Missing Configuration File
- **Scenario**: Config file doesn't exist
- **Expected**: `FileNotFoundError` with helpful message
- **Test**: `test_nonexistent_config_file()`

#### Test Case: Malformed YAML
- **Scenario**: Invalid YAML syntax
- **Expected**: YAML parser error
- **Test**: Manual verification required

#### Test Case: Missing Required Keys
- **Scenario**: Config missing critical parameters
- **Expected**: Default values used or clear error
- **Test**: `test_get_with_default()`

---

## 4. Running Tests

### 4.1 Prerequisites

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4.2 Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agents.py

# Run specific test
pytest tests/test_agents.py::TestBaseAgent::test_validate_input_valid
```

### 4.3 Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage report
open results/coverage/html/index.html

# Generate XML for CI/CD
pytest --cov=src --cov-report=xml
```

### 4.4 Test with Different Python Versions

```bash
# Using tox (if configured)
tox

# Using pyenv
pyenv local 3.8 3.9 3.10
python3.8 -m pytest
python3.9 -m pytest
python3.10 -m pytest
```

---

## 5. CI/CD Integration

### 5.1 GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### 5.2 Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

---

## 6. Expected Test Results

### 6.1 Success Criteria

- ✅ All tests pass (100% pass rate)
- ✅ Code coverage ≥ 85%
- ✅ No critical linter errors
- ✅ Test execution time < 60 seconds

### 6.2 Acceptable Failures

Some scenarios where test failures are expected and acceptable:

1. **External CLI Not Installed**: Tests requiring actual CLI tools will fail if not installed
   - Solution: Mock tests or skip with `@pytest.mark.skipif`

2. **Network Unavailable**: Model downloads fail
   - Solution: Cache models or use mock embeddings

3. **Platform-Specific**: Some tests may be OS-dependent
   - Solution: Use `@pytest.mark.skipif(sys.platform != 'linux')`

---

## 7. Test Maintenance

### 7.1 Adding New Tests

When adding new features:

1. Write tests BEFORE implementation (TDD)
2. Ensure edge cases are covered
3. Update this document with new edge cases
4. Verify coverage doesn't drop below 85%

### 7.2 Updating Tests

When modifying code:

1. Update affected tests
2. Re-run full test suite
3. Check coverage impact
4. Document any new edge cases

### 7.3 Test Review Checklist

Before merging:

- [ ] All tests pass
- [ ] Coverage ≥ 85%
- [ ] New edge cases documented
- [ ] Test names are descriptive
- [ ] Mock dependencies appropriately
- [ ] No test interdependencies
- [ ] Tests run in reasonable time

---

## 8. Known Limitations

### 8.1 Current Test Gaps

1. **Real LLM Testing**: Tests use mocks, not actual CLI tools
   - Reason: Avoid external dependencies and costs
   - Mitigation: Integration tests run separately

2. **Large-Scale Performance**: Not tested with 1000s of sentences
   - Reason: Time constraints
   - Mitigation: Performance benchmarks separate from unit tests

3. **Concurrency**: Limited multi-threading/multi-processing tests
   - Reason: Complexity
   - Mitigation: Sequential execution is sufficient for research

### 8.2 Future Improvements

1. Add integration tests with real CLI tools (optional, slow)
2. Add performance benchmarking suite
3. Add stress tests for database
4. Add property-based testing (Hypothesis)
5. Add mutation testing to verify test quality

---

## 9. Troubleshooting

### Issue: Tests Hang
**Cause**: Subprocess timeout not configured
**Solution**: Set `timeout` parameter or use `pytest-timeout`

### Issue: Coverage Lower Than Expected
**Cause**: Untested code paths
**Solution**: Run `pytest --cov=src --cov-report=term-missing` to see missing lines

### Issue: Import Errors
**Cause**: PYTHONPATH not set correctly
**Solution**: Run from project root or install package in dev mode: `pip install -e .`

### Issue: Database Locked
**Cause**: Concurrent access without proper handling
**Solution**: Enable WAL mode in SQLite configuration

---

## 10. References

1. pytest documentation: https://docs.pytest.org/
2. pytest-cov documentation: https://pytest-cov.readthedocs.io/
3. unittest.mock guide: https://docs.python.org/3/library/unittest.mock.html
4. Test-Driven Development by Kent Beck

---

**Document Version:** 1.0  
**Last Updated:** November 18, 2025  
**Maintained By:** Project Team

