# tools.py
import inspect
import json
from typing import Callable, Dict, Any

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: list = []

    def register(self, func: Callable):
        """Decorator to register a python function as an agent tool."""
        name = func.__name__
        self.tools[name] = func
        
        sig = inspect.signature(func)
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
                
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)

        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": func.__doc__ or "No description provided.",
                "parameters": parameters
            }
        }
        self.schemas.append(schema)
        return func

# --- CRITICAL: This line must be present at the bottom of tools.py ---
registry = ToolRegistry()