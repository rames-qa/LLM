# server.py
import json
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from orchestrator import AgentOrchestrator
from tools import registry
import custom_tools  # noqa: F401 - Ensures all @registry.register decorators execute

app = FastAPI(title="LLM Automation Framework")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent session store for multi-turn memory
sessions: Dict[str, AgentOrchestrator] = {}

def get_or_create_agent(session_id: str) -> AgentOrchestrator:
    if session_id not in sessions:
        sessions[session_id] = AgentOrchestrator()
    return sessions[session_id]

class GoalRequest(BaseModel):
    goal: str
    session_id: str = "default"

@app.get("/tools")
def get_registered_tools():
    """Exposes registered Python tools to the frontend dynamically."""
    return {"tools": registry.metadata}

@app.post("/reset/{session_id}")
def reset_session(session_id: str):
    """Clears conversation memory for a session."""
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "cleared", "session_id": session_id}

@app.post("/run-agent-stream")
def run_agent_stream(request: GoalRequest):
    """Streams live ReAct steps (Thinking -> Tool Call -> Observation -> Final) via SSE."""
    agent = get_or_create_agent(request.session_id)

    def event_generator():
        for event in agent.run_stream(user_goal=request.goal):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
