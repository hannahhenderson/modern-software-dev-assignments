# Adding New AI Backends

The refactored client uses pure functional programming with function factories. Here's how to add new backends:

## Current Backends

```python
# Backend processor factory functions
processor_factories = {
    'ollama_dev': lambda: create_ollama_processor(
        model=os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
    ),
    'claude_cheaper': lambda: create_claude_processor(
        model='claude-haiku-20240307',
        max_tokens=300
    ),
    'claude_expensive': lambda: create_claude_processor(
        model='claude-sonnet-4-5',
        max_tokens=1000
    )
}
```

## Adding a New Backend

### 1. Create the Processor Function

```python
def create_openai_processor(model: str, max_tokens: int):
    """Create an OpenAI processor using pure functional composition"""
    openai = OpenAI()
    
    async def process_query(query: str, available_tools: list, session: ClientSession) -> str:
        """Process query using OpenAI"""
        messages = [{"role": "user", "content": query}]

        # OpenAI API call
        response = openai.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []
        for choice in response.choices:
            if choice.message.content:
                final_text.append(choice.message.content)
            
            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Execute tool call
                    result = await session.call_tool(tool_name, tool_args)
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                    final_text.append(f"Result: {result.content}")

        return "\n".join(final_text)
    
    return process_query  # Returns a function, not a class
```

### 2. Add to Factory Functions

```python
processor_factories = {
    # ... existing backends ...
    'openai_cheaper': lambda: create_openai_processor(
        model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '500'))
    ),
    'openai_expensive': lambda: create_openai_processor(
        model=os.getenv('OPENAI_MODEL', 'gpt-4'),
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
    )
}
```

### 3. Use the New Backend

```bash
AI_BACKEND=openai_cheaper python client/ai_mcp_client.py ../server/petting_zootopia.py
```

## Benefits of This Functional Design

- ✅ **Zero classes** - pure functional programming
- ✅ **Function factories** - create configured functions
- ✅ **Closures** - capture state without classes
- ✅ **Higher-order functions** - functions that return functions
- ✅ **Function composition** - combine functions elegantly
- ✅ **Pure functions** - no side effects
- ✅ **Easy to extend** - just add to factory functions

## Adding Environment Variables

```python
# In the factory functions
'openai_cheaper': lambda: create_openai_processor(
    model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
    max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '500'))
)
```

## Example: Adding a Local Model Backend

```python
def create_local_llm_processor(model_path: str, max_tokens: int):
    """Create a local LLM processor"""
    # Initialize local model
    local_model = load_model(model_path)
    
    async def process_query(query: str, available_tools: list, session: ClientSession) -> str:
        """Process query using local model"""
        # Local model implementation
        response = local_model.generate(query, max_tokens=max_tokens)
        return response
    
    return process_query

# Add to factories
processor_factories['local_llm'] = lambda: create_local_llm_processor(
    model_path=os.getenv('LOCAL_MODEL_PATH', './models/llama'),
    max_tokens=int(os.getenv('LOCAL_MAX_TOKENS', '512'))
)
```

This functional design is much cleaner and more maintainable! 🎉
