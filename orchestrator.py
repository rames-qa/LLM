# In orchestrator.py
from openai import OpenAI

class AgentOrchestrator:
    def __init__(self, system_prompt: str = "You are a helpful automation assistant."):
        # Point the OpenAI client to your local Ollama server
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama" # Ollama doesn't check the key, but the SDK requires a string
        )
        self.messages = [{"role": "system", "content": system_prompt}]
        self.model = "llama3.2" # Use the local model you pulled
