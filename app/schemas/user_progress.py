from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum



class UserProgressBase(BaseModel):
    choice_node: Optional[Dict[str, Any]] = None
    is_completed: bool = False

class UserProgressCreate(UserProgressBase):
    user_id: int
    story_id: int
    current_node_id: int

class UserProgressUpdate(BaseModel):
    current_node_id: Optional[int] = None
    choice_node: Optional[Dict[str, Any]] = None
    is_completed: Optional[bool] = None

class UserProgressResponse(UserProgressBase):
    progress_id: int
    user_id: int
    story_id: int
    current_node_id: int
    start_time: datetime
    last_updated : datetime
    
    class Config:
        from_attributes = True