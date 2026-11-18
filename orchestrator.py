# orchestrator.py
import json
from typing import Generator, Dict, Any
from openai import OpenAI
from tools import registry

DEFAULT_SYSTEM_PROMPT = """You are an autonomous ReAct automation agent.
You have access to local tools to inspect files, write reports, and calculate metrics.
- Always break complex goals into steps.
- Use your tools to gather facts before answering.
- If a user asks you to save or document results, use `write_text_file`.
- Provide a clear, concise final summary once all tool steps are complete."""

class AgentOrchestrator:
    def __init__(
        self,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        model: str = "llama3.2",
        max_iterations: int = 8
    ):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
        self.model = model
        self.max_iterations = max_iterations
        self.messages = [{"role": "system", "content": system_prompt}]

    def run_stream(self, user_goal: str) -> Generator[Dict[str, Any], None, None]:
        """Executes the ReAct tool-calling loop and yields step-by-step events."""
        self.messages.append({"role": "user", "content": user_goal})

        for step in range(1, self.max_iterations + 1):
            yield {"type": "thinking", "step": step, "content": f"Step {step}: Reasoning..."}

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=registry.schemas if registry.schemas else None,
                    tool_choice="auto" if registry.schemas else None,
                )
            except Exception as e:
                yield {"type": "error", "content": f"Ollama API Error: {str(e)}"}
                return

            message = response.choices[0].message
            
            # Append assistant message (including any tool_calls) to memory
            assistant_msg_dict = {"role": "assistant", "content": message.content or ""}
            if message.tool_calls:
                assistant_msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            self.messages.append(assistant_msg_dict)

            # If the model decided to call tools:
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    fn_name = tool_call.function.name
                    raw_args = tool_call.function.arguments
                    
                    try:
                        parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except json.JSONDecodeError:
                        parsed_args = {}

                    yield {
                        "type": "tool_call",
                        "step": step,
                        "tool": fn_name,
                        "args": parsed_args
                    }

                    # Execute the actual Python function from custom_tools.py
                    observation = registry.execute(fn_name, parsed_args)

                    yield {
                        "type": "tool_result",
                        "step": step,
                        "tool": fn_name,
                        "output": observation
                    }

                    # Feed observation back to the LLM
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": fn_name,
                        "content": observation
                    })
            else:
                # No tool calls means the agent has reached its final answer
                final_text = message.content or "Task completed."
                yield {"type": "final", "content": final_text}
                return

        yield {
            "type": "final",
            "content": "Reached maximum reasoning iterations without a final conclusion."
        }

    def run(self, user_goal: str) -> str:
        """Synchronous helper for CLI execution (main.py)."""
        final_output = ""
        for event in self.run_stream(user_goal):
            if event["type"] == "tool_call":
                print(f"  [Action] {event['tool']}({event['args']})")
            elif event["type"] == "tool_result":
                print(f"  [Observation] {event['output']}")
            elif event["type"] == "final":
                final_output = event["content"]
                print(f"\n[Final Answer]\n{final_output}")
            elif event["type"] == "error":
                print(f"\n[Error] {event['content']}")
        return final_output
