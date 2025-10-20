"""
Simple Honeycomb.io instrumentation following official documentation
"""

import os
from opentelemetry import trace

# Simple tracer setup following Honeycomb docs
tracer = trace.get_tracer("petting-zootopia-mcp")

def trace_tool(operation_name: str):
    """Simple decorator following Honeycomb's examples"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(operation_name) as span:
                # Add basic attributes as shown in Honeycomb docs
                span.set_attribute("tool.name", operation_name)
                span.set_attribute("service.name", "petting-zootopia-mcp")
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error", str(e))
                    span.recordException(e)
                    raise
        return wrapper
    return decorator
