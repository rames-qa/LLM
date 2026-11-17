# main.py
from dotenv import load_dotenv
load_dotenv()  # This must run before importing orchestrator or custom_tools

from orchestrator import AgentOrchestrator
import custom_tools  # noqa

if __name__ == "__main__":
    agent = AgentOrchestrator(
        system_prompt="You are an autonomous assistant. Use your tools to fulfill user goals step by step."
    )
    
    goal = "Calculate the metrics for these numbers: 10, 25, 40, 55, 70"
    agent.run(user_goal=goal)