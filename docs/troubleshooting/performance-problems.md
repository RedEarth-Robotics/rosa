# Performance Problems

Optimizing ROSA performance and resource usage.

## Quick Diagnostics

```python
import time

start = time.time()
response = rosa.invoke("List all topics")
duration = time.time() - start
print(f"Response time: {duration:.2f} seconds")
```

## Common Problems

### Problem: Slow responses

**Symptoms**:
Responses take more than 10 seconds.

**Solutions**:

1. **Use non-streaming mode**:
```python
rosa = ROSA(ros_version=1, llm=llm, streaming=False)
```

2. **Use faster model**:
```python
# GPT-3.5 is faster than GPT-4
llm = ChatOpenAI(model="gpt-3.5-turbo")
```

3. **Limit iterations**:
```python
rosa = ROSA(ros_version=1, llm=llm, max_iterations=10)
```

4. **Optimize queries**:
```python
# Instead of:
rosa.invoke("Can you please list all the topics that are currently available in the system?")

# Use:
rosa.invoke("List all topics")
```

### Problem: High token usage

**Symptoms**:
High API costs or token limit errors.

**Solutions**:

1. **Track token usage**:
```python
rosa = ROSA(
    ros_version=1,
    llm=llm,
    show_token_usage=True,
    streaming=False
)
```

2. **Clear chat history**:
```python
rosa.clear_chat()
```

3. **Disable history accumulation**:
```python
rosa = ROSA(ros_version=1, llm=llm, accumulate_chat_history=False)
```

4. **Use shorter queries**:
```python
# Concise queries use fewer tokens
rosa.invoke("List nodes")
```

### Problem: High memory usage

**Symptoms**:
System runs out of memory.

**Solutions**:

1. **Clear chat history regularly**:
```python
rosa.clear_chat()
```

2. **Disable intermediate steps**:
```python
rosa = ROSA(ros_version=1, llm=llm, return_intermediate_steps=False)
```

3. **Limit tool output**:
```python
rosa.invoke("List first 10 topics")
```

### Problem: Network latency

**Symptoms**:
Slow responses due to network issues.

**Solutions**:

1. **Use local models**:
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1")
```

2. **Set timeout**:
```python
llm = ChatOpenAI(request_timeout=10)
```

3. **Check network**:
```bash
ping api.openai.com
```

## Optimization Strategies

### Caching Responses

```python
from functools import lru_cache

class CachedROSA(ROSA):
    @lru_cache(maxsize=100)
    def cached_invoke(self, query: str) -> str:
        return self.invoke(query)
```

### Batch Processing

```python
queries = [
    "List nodes",
    "List topics", 
    "List services"
]

results = []
for query in queries:
    results.append(rosa.invoke(query))
```

### Connection Pooling

```python
# Reuse LLM connection
llm = ChatOpenAI(model="gpt-4")

# Create multiple ROSA instances with same LLM
rosa1 = ROSA(ros_version=1, llm=llm)
rosa2 = ROSA(ros_version=1, llm=llm)
```

## Monitoring

### Track Performance

```python
import time

class PerformanceMonitor:
    def __init__(self):
        self.measurements = []
    
    def measure(self, rosa, query):
        start = time.time()
        response = rosa.invoke(query)
        duration = time.time() - start
        
        self.measurements.append({
            "query": query,
            "duration": duration,
            "response_length": len(response)
        })
        
        return response
    
    def report(self):
        avg_duration = sum(m["duration"] for m in self.measurements) / len(self.measurements)
        print(f"Average response time: {avg_duration:.2f} seconds")
```

## Next Steps

- [Debugging Tools](debugging-tools.md)
- [Configuration Guide](../core/configuration.md)
- [Advanced Agent Tutorial](../tutorials/advanced-agent-customization.md)
