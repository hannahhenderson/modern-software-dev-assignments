# 🧪 Petting Zootopia Test Suite

Comprehensive testing for the MCP application with graceful failure handling and cost-conscious AI backend testing.

## 📋 Test Categories

### **1. 🌐 Web Client Tests (`test_web_app.py`)**
- **MCP Integration**: Web app ↔ MCP client communication
- **Graceful Failure**: Sad animal images on errors
- **Error Scenarios**: 
  - MCP client not initialized
  - MCP server connection failure
  - External API timeouts
  - Tool execution failures
  - Invalid requests
  - Concurrent request failures

### **2. 🛠️ MCP Server Tools (`test_mcp_tools.py`)**
- **Individual Tools**: `greet()`, `duck()`, `dog()`, `cat()`
- **External API Integration**: random-d.uk, dog.ceo, thecatapi.com
- **Error Handling**: Timeouts, rate limiting, network failures
- **Edge Cases**: Invalid JSON, missing fields, empty responses

### **3. 🤖 AI Backend Tests (`test_ai_backends.py`)**
- **Ollama Backend**: Free, local testing (always runs)
- **Claude Backend**: Cost-conscious testing (disabled by default)
- **Backend Selection**: Environment variable configuration
- **Error Handling**: API failures, rate limiting, timeouts

### **4. 🔄 End-to-End Tests (`test_e2e.py`)**
- **User Journey**: Button click → Animal image
- **MCP Integration**: Client ↔ Server communication
- **Concurrent Users**: Multiple simultaneous requests
- **Error Recovery**: System recovery after failures
- **Web Interface**: Landing page, health checks, static assets

### **5. 🧠 LLM Parsing Tests (`test_mcp_client_llm.py`)**
- **Accuracy Testing**: Multiple runs for statistical significance
- **Gibberish Handling**: Extract animals from random text
- **Unsupported Animals**: Graceful handling of invalid requests
- **Performance**: Response time and accuracy metrics

## 🚀 Running Tests

### **Quick Test Run (Free)**
```bash
# Run all tests except Claude (no cost)
./run_tests.sh
```

### **Individual Test Categories**
```bash
# Web client tests (includes graceful failure)
pytest tests/test_web_app.py -v

# MCP server tools
pytest tests/test_mcp_tools.py -v

# AI backends (Ollama only)
pytest tests/test_ai_backends.py -v

# End-to-end user journey
pytest tests/test_e2e.py -v

# LLM parsing accuracy
pytest tests/test_mcp_client_llm.py -v -s
```

### **Claude Tests (Costs Money)**
```bash
# ⚠️ WARNING: This will consume Claude API credits
ENABLE_CLAUDE_TESTS=true pytest tests/test_ai_backends.py -v

# Estimated cost: ~$0.01-0.05 per run
```

## 🎯 Test Scenarios

### **Graceful Failure Tests**
The web client tests include comprehensive graceful failure scenarios:

1. **MCP Client Not Initialized**
   - User sees: Sad animal image + "The animals are all sleeping" message
   - API returns: 500 error with helpful message

2. **MCP Server Connection Failure**
   - User sees: Sad animal image + error message
   - API returns: 500 error with connection details

3. **External API Timeout**
   - User sees: Sad animal image + "Please try again later"
   - API returns: 500 error with timeout details

4. **Tool Execution Failure**
   - User sees: Sad animal image + error message
   - API returns: 500 error with execution details

5. **Invalid Requests**
   - User sees: Validation error message
   - API returns: 400 error with field details

6. **Concurrent Request Failure**
   - User sees: Sad animal image + "System busy" message
   - API returns: 500 error with resource details

### **AI Backend Cost Protection**
The AI backend tests are designed to protect your Claude credits:

- **Ollama Tests**: Always run (free, local)
- **Claude Tests**: Disabled by default, require explicit opt-in
- **Environment Check**: Tests skip if API key not set
- **Cost Warnings**: Clear messaging about potential charges

## 📊 Test Coverage

### **High Priority (Must Pass)**
- ✅ Web interface loads and responds
- ✅ MCP client connects to server
- ✅ Animal buttons return images
- ✅ Error scenarios show sad animals
- ✅ Invalid requests are rejected

### **Medium Priority (Should Pass)**
- ✅ External APIs handle failures gracefully
- ✅ Concurrent users don't break system
- ✅ MCP tools work with real APIs
- ✅ AI backends process queries correctly

### **Low Priority (Nice to Have)**
- ✅ LLM parsing accuracy > 80%
- ✅ Performance under load
- ✅ Error recovery scenarios
- ✅ Multiple AI backend support

## 🔧 Test Configuration

### **Environment Variables**
```bash
# For Claude tests (optional)
export ENABLE_CLAUDE_TESTS=true
export ANTHROPIC_API_KEY=your_key_here

# For Ollama tests (optional)
export OLLAMA_MODEL=llama3.2:3b
```

### **Test Dependencies**
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Or use the test runner
./run_tests.sh
```

## 🐛 Debugging Tests

### **Verbose Output**
```bash
# Run with detailed output
pytest tests/test_web_app.py -v -s

# Run specific test
pytest tests/test_web_app.py::TestWebAppGracefulFailure::test_mcp_client_not_initialized -v
```

### **Test Isolation**
```bash
# Run tests in isolation
pytest tests/test_web_app.py -v --tb=short

# Stop on first failure
pytest tests/test_web_app.py -v -x
```

## 📈 Expected Results

### **Success Criteria**
- All web client tests pass
- All MCP tool tests pass
- All end-to-end tests pass
- Graceful failure tests show sad animals
- AI backend tests work (Ollama) or skip (Claude)

### **Performance Targets**
- Web response time < 2 seconds
- MCP client connection < 1 second
- LLM parsing accuracy > 80%
- Error recovery < 5 seconds

## 🚨 Troubleshooting

### **Common Issues**
1. **MCP Client Connection**: Ensure server is running
2. **External API Failures**: Check internet connection
3. **Claude Test Failures**: Verify API key and credits
4. **Ollama Test Failures**: Ensure Ollama is running

### **Test Debugging**
```bash
# Run with debug output
pytest tests/test_web_app.py -v -s --tb=long

# Check specific failure
pytest tests/test_web_app.py::TestWebAppGracefulFailure -v
```

## 💡 Best Practices

1. **Run tests before deployment**
2. **Use graceful failure tests for user experience**
3. **Protect Claude credits with environment checks**
4. **Test error scenarios thoroughly**
5. **Monitor test performance and accuracy**

This test suite ensures your MCP application is robust, user-friendly, and cost-conscious! 🎉