# orchestrator.py
import os
import json
from openai import OpenAI
from tools import registry
import custom_tools  # noqa: imports and registers tools

class AgentOrchestrator:
    def __init__(self, system_prompt: str = "You are a helpful automation assistant."):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.messages = [{"role": "system", "content": system_prompt}]
        self.model = "gpt-4o-mini" # or any tool-capable model

    def run(self, user_goal: str, max_iterations: int = 5):
        self.messages.append({"role": "user", "content": user_goal})
        
        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Call LLM with available tool schemas
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=registry.schemas,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            self.messages.append(response_message)
            
            # Check if the model wants to call a tool
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    print(f"[Action] Calling tool '{func_name}' with args: {func_args}")
                    
                    if func_name in registry.tools:
                        # Execute the local python function
                        tool_result = registry.tools[func_name](**func_args)
                    else:
                        tool_result = f"Error: Tool {func_name} not found."
                        
                    print(f"[Observation] {tool_result}")
                    
                    # Feed the tool observation back into conversation history
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": str(tool_result)
                    })
            else:
                # No tool called; final answer reached
                print(f"\n[Final Answer]\n{response_message.content}")
                return response_message.content

        print("Max iterations reached without final resolution.")
        return None