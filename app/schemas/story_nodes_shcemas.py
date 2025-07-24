from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class StoryNodeBase(BaseModel):
    node_title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    is_starting_node: bool = False
    is_ending_node: bool = False
    node_type: Literal["story", "choice", "ending"]  # simple validation, no Enum

class StoryNodeCreate(StoryNodeBase):
    story_id: int

class StoryNodeUpdate(BaseModel):
    node_title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    is_starting_node: Optional[bool] = None
    is_ending_node: Optional[bool] = None
    node_type: Optional[str] = None

class StoryNodeResponse(StoryNodeBase):
    node_id: int
    story_id: int
    
    class Config:
        from_attributes = True