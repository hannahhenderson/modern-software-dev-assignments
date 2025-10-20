# Petting Zootopia Test Suite

This directory contains comprehensive tests for the Petting Zootopia MCP project.

## 🧪 Test Coverage

### 1. Web App MCP Integration Tests (`test_web_app.py`)
- ✅ **Web app sends correct info to MCP client** - Verifies proper data flow
- ✅ **Error handling** - Tests graceful error handling
- ✅ **Invalid animal types** - Tests input validation
- ✅ **MCP client exceptions** - Tests exception handling

### 2. MCP Client LLM Parsing Tests (`test_mcp_client_llm.py`)
- ✅ **LLM accuracy testing** - Runs queries multiple times to measure accuracy
- ✅ **Gibberish parsing** - Tests extraction from malformed input
- ✅ **Unsupported animals** - Tests handling of invalid requests
- ✅ **Non-animal requests** - Tests general conversation handling

### 3. Error Handling with Sad Animals
- ✅ **Sad cat image** - Displayed when cat requests fail
- ✅ **Sad dog image** - Displayed when dog requests fail  
- ✅ **Sad duck image** - Displayed when duck requests fail

## 🚀 Running Tests

### Quick Test Run
```bash
# Run all tests
./run_tests.sh

# Or run specific test files
pytest tests/test_web_app.py -v
pytest tests/test_mcp_client_llm.py -v -s
```

### Individual Test Categories
```bash
# Web app integration tests
pytest tests/test_web_app.py::TestWebAppMCPIntegration -v

# LLM parsing accuracy tests
pytest tests/test_mcp_client_llm.py::TestMCPClientLLMParsing -v -s

# Error handling tests
pytest tests/test_web_app.py::TestWebAppErrorHandling -v
```

## 📊 Test Results

The LLM parsing tests will output detailed accuracy results:

```
============================================================
LLM PARSING ACCURACY RESULTS
============================================================
Overall Accuracy: 85.00% (51/60)

Detailed Results:
Query                          Expected   Accuracy   Predictions
--------------------------------------------------------------------------------
I want a cat                   cat        100.00%    cat, cat, cat
I want a dog                   dog        100.00%    dog, dog, dog
isdkalsfdha cat               cat        100.00%    cat, cat, cat
I want an elephant            None       100.00%    None, None, None
```

## 🎯 Test Requirements Met

### ✅ Web App MCP Integration
- Web app correctly sends information to MCP client
- Proper error handling and user feedback
- Graceful degradation with sad animal images

### ✅ LLM Parsing Accuracy
- Tests run multiple times to measure consistency
- Handles gibberish input correctly
- Distinguishes between supported/unsupported animals
- Maintains high accuracy across different query types

### ✅ Error Handling
- Sad animal images displayed on failures
- User-friendly error messages
- Graceful fallbacks for all animal types

## 🔧 Test Configuration

### Environment Variables
```bash
# For testing with different AI backends
export AI_BACKEND=ollama_dev
export AI_BACKEND=claude_cheaper
export AI_BACKEND=claude_expensive
```

### Test Data
- **Valid queries**: 9 different animal request patterns
- **Gibberish queries**: 5 malformed inputs
- **Unsupported animals**: 4 invalid animal types
- **Non-animal requests**: 4 general conversation queries

## 📈 Success Criteria

- **Overall LLM Accuracy**: ≥ 70%
- **Web App Integration**: All tests pass
- **Error Handling**: Sad animals displayed correctly
- **Input Validation**: Proper handling of invalid inputs

## 🐛 Debugging Tests

### Verbose Output
```bash
pytest tests/ -v -s --tb=short
```

### Specific Test Debugging
```bash
pytest tests/test_mcp_client_llm.py::TestMCPClientLLMParsing::test_llm_parsing_accuracy_multiple_runs -v -s
```

### Mock Testing
```bash
# Test with mocked MCP client
pytest tests/test_web_app.py::TestWebAppMCPIntegration::test_web_app_sends_correct_info_to_mcp_client -v
```
