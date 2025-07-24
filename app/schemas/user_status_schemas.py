from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserStatsBase(BaseModel):
    stories_completed: int = 0
    total_choices_made: int = 0
    favorite_category: str = ""
    total_play_time: int = 0  # in minutes

class UserStatsResponse(UserStatsBase):
    stat_id: int
    user_id: int
    
    class Config:
        from_attributes = True

class UserStatsUpdate(BaseModel):
    stories_completed: Optional[int] = None
    total_choices_made: Optional[int] = None
    favorite_category: Optional[str] = None
    total_play_time: Optional[int] = None
