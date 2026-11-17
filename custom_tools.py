# custom_tools.py
from tools import registry

@registry.register
def read_text_file(filepath: str) -> str:
    """Reads content from a local text file given its path."""
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@registry.register
def calculate_metrics(data_points: str) -> str:
    """Calculates basic stats from a comma-separated list of numbers."""
    try:
        numbers = [float(x.strip()) for x in data_points.split(",")]
        return f"Count: {len(numbers)}, Sum: {sum(numbers)}, Average: {sum(numbers)/len(numbers)}"
    except Exception as e:
        return f"Error parsing numbers: {str(e)}"