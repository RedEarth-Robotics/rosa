# LLM Provider Issues

Solving problems with language model providers.

## Quick Diagnostics

```python
# Test LLM connection
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
try:
    response = llm.invoke("Hello")
    print("LLM connection successful")
except Exception as e:
    print(f"LLM connection failed: {e}")
```

## Common Problems

### Problem: API key not found

**Symptoms**:
```
AuthenticationError: No API key provided
```

**Solutions**:

1. **Set environment variable**:
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

2. **Use .env file**:
```bash
# .env
OPENAI_API_KEY=sk-...
```
```python
from dotenv import load_dotenv
load_dotenv()
```

3. **Pass directly** (not recommended):
```python
llm = ChatOpenAI(api_key="sk-...")
```

### Problem: Rate limit exceeded

**Symptoms**:
```
RateLimitError: Too many requests
```

**Solutions**:

1. **Implement retry logic**:
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(max_retries=5, request_timeout=30)
```

2. **Add delays between requests**:
```python
import time
time.sleep(1)  # Wait 1 second between requests
```

3. **Check usage dashboard**:
- OpenAI: https://platform.openai.com/usage
- Anthropic: https://console.anthropic.com/settings/usage

### Problem: Model not available

**Symptoms**:
```
NotFoundError: The model does not exist
```

**Solutions**:

1. **Check model name**:
```python
# Correct
ChatOpenAI(model="gpt-4")

# Incorrect
ChatOpenAI(model="gpt4")
```

2. **Verify model access**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

3. **Use fallback model**:
```python
try:
    llm = ChatOpenAI(model="gpt-4")
except:
    llm = ChatOpenAI(model="gpt-3.5-turbo")
```

### Problem: High costs

**Solutions**:

1. **Track usage**:
```python
rosa = ROSA(
    ros_version=1,
    llm=llm,
    show_token_usage=True,
    streaming=False
)
```

2. **Use cheaper model**:
```python
llm = ChatOpenAI(model="gpt-3.5-turbo")  # Cheaper than gpt-4
```

3. **Limit iterations**:
```python
rosa = ROSA(ros_version=1, llm=llm, max_iterations=10)
```

### Problem: Ollama connection failed

**Symptoms**:
```
ConnectionError: Can't connect to Ollama
```

**Solutions**:

1. **Start Ollama**:
```bash
ollama serve
```

2. **Check if model exists**:
```bash
ollama list
ollama pull llama3.1
```

3. **Verify port**:
```bash
curl http://localhost:11434/api/tags
```

### Problem: Azure OpenAI issues

**Symptoms**:
```
AuthenticationError with Azure
```

**Solutions**:

1. **Check environment variables**:
```bash
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://..."
export AZURE_OPENAI_API_VERSION="2024-02-01"
```

2. **Verify deployment**:
```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment="your-deployment-name",
    api_version="2024-02-01"
)
```

## Provider Comparison

| Provider | Setup Complexity | Cost | Speed | Reliability |
|----------|-----------------|------|-------|-------------|
| OpenAI | Easy | Medium | Fast | High |
| Anthropic | Easy | Medium | Fast | High |
| Azure | Medium | Medium | Fast | High |
| Ollama | Medium | Free | Slow | Local |

## Next Steps

- [Performance Problems](performance-problems.md)
- [Configuration Guide](../core/configuration.md)
- [API Reference](../core/api-reference.md)
