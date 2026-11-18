# custom_tools.py
import os
import statistics
from pathlib import Path
from tools import registry

# Create a safe sandbox directory for agent file operations
WORKSPACE_DIR = Path("./agent_workspace").resolve()
WORKSPACE_DIR.mkdir(exist_ok=True)

def _safe_path(filepath: str) -> Path:
    """Prevents directory traversal outside WORKSPACE_DIR."""
    target = (WORKSPACE_DIR / filepath).resolve()
    if not str(target).startswith(str(WORKSPACE_DIR)):
        raise PermissionError("Access denied: Path escapes agent_workspace sandbox.")
    return target

@registry.register(icon="fa-folder-open")
def list_workspace_files() -> str:
    """Lists all files currently available in the agent workspace."""
    files = [f.name for f in WORKSPACE_DIR.iterdir() if f.is_file()]
    return f"Workspace files: {', '.join(files)}" if files else "Workspace is currently empty."

@registry.register(icon="fa-file-lines")
def read_text_file(filepath: str) -> str:
    """Reads content from a file inside the agent workspace.
    :param filepath: Relative filename inside the workspace (e.g., 'data.txt').
    """
    target = _safe_path(filepath)
    if not target.exists():
        return f"Error: File '{filepath}' does not exist in workspace."
    return target.read_text(encoding="utf-8")

@registry.register(icon="fa-file-pen")
def write_text_file(filepath: str, content: str) -> str:
    """Writes or overwrites text content to a file inside the agent workspace.
    :param filepath: Relative filename to create or overwrite (e.g., 'report.md').
    :param content: The text content to write into the file.
    """
    target = _safe_path(filepath)
    target.write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} characters to '{filepath}'."

@registry.register(icon="fa-calculator")
def calculate_metrics(data_points: str) -> str:
    """Calculates comprehensive statistics from a comma-separated list of numbers.
    :param data_points: Comma-separated numbers (e.g., '10, 25, 40, 55, 70').
    """
    numbers = [float(x.strip()) for x in data_points.split(",") if x.strip()]
    if not numbers:
        return "Error: No valid numbers provided."
    
    return (
        f"Count: {len(numbers)} | "
        f"Sum: {sum(numbers):.2f} | "
        f"Mean: {statistics.mean(numbers):.2f} | "
        f"Median: {statistics.median(numbers):.2f} | "
        f"Min: {min(numbers):.2f} | "
        f"Max: {max(numbers):.2f}"
    )
