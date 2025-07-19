"""Extract tasks and deadlines from text."""
import re
from typing import List, Dict

DATE_PATTERN = r"\d{1,2}\.\d{1,2}\.\d{4}"
TASK_PATTERN = re.compile(r"(?P<task>[^.]*?)\s+bis\s+(?P<date>" + DATE_PATTERN + r")", re.IGNORECASE)

def extract_tasks(text: str) -> List[Dict[str, str]]:
    tasks = []
    for match in TASK_PATTERN.finditer(text):
        task = match.group("task").strip()
        date = match.group("date")
        tasks.append({"task": task, "due": date})
    return tasks
