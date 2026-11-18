# tools.py
import inspect
import json
import re
from typing import Callable, Dict, Any, List, get_type_hints

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: List[Dict[str, Any]] = []
        self.metadata: List[Dict[str, str]] = []

    def _parse_docstring_params(self, docstring: str) -> Dict[str, str]:
        """Extracts ':param name: description' lines from a function's docstring."""
        if not docstring:
            return {}
        matches = re.findall(r":param\s+(\w+):\s*(.+)", docstring)
        return {name: desc.strip() for name, desc in matches}

    def register(self, icon: str = "fa-wrench"):
        """Decorator factory to register a python function as an agent tool with UI metadata."""
        def decorator(func: Callable):
            name = func.__name__
            self.tools[name] = func
            
            raw_doc = inspect.getdoc(func) or "No description provided."
            # Clean summary (first paragraph before :param)
            summary = raw_doc.split(":param")[0].strip()
            param_docs = self._parse_docstring_params(raw_doc)
            type_hints = get_type_hints(func)

            sig = inspect.signature(func)
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            type_map = {
                int: "integer",
                float: "number",
                bool: "boolean",
                str: "string",
                list: "array",
                dict: "object"
            }

            for param_name, param in sig.parameters.items():
                py_type = type_hints.get(param_name, str)
                json_type = type_map.get(py_type, "string")
                    
                parameters["properties"][param_name] = {
                    "type": json_type,
                    "description": param_docs.get(param_name, f"Parameter {param_name}")
                }
                if param.default == inspect.Parameter.empty:
                    parameters["required"].append(param_name)

            schema = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": summary,
                    "parameters": parameters
                }
            }
            self.schemas.append(schema)
            self.metadata.append({
                "name": name,
                "description": summary,
                "icon": icon,
                "parameters": list(parameters["properties"].keys())
            })
            return func
        return decorator

    def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        """Safely executes a registered tool and returns stringified output."""
        if name not in self.tools:
            return f"Error: Tool '{name}' is not registered."
        try:
            result = self.tools[name](**arguments)
            return str(result)
        except Exception as e:
            return f"Tool Execution Error ({name}): {str(e)}"

registry = ToolRegistry()
