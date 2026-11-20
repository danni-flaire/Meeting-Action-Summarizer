from pydantic import BaseModel, Field
from typing import List

class MeetingInput(BaseModel):
    transcript: str

class ActionItem(BaseModel):
    task: str
    owner: str
    deadline: str

class MeetingOutput(BaseModel):
    meeting_summary: str
    key_decisions: List[str]
    action_items: List[ActionItem]