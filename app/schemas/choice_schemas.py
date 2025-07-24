from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class ChoiceBase(BaseModel):
    choice_text: str = Field(..., min_length=1, max_length=500)
    choice_letter: str = Field(..., pattern=r'^[A-D]$') 

    consequences: Optional[str] = None

class ChoiceCreate(ChoiceBase):
    from_node_id: int
    to_node_id: int

class ChoiceUpdate(BaseModel):
    choice_text: Optional[str] = Field(None, min_length=1, max_length=500)
    choice_letter: Optional[str] = Field(None, pattern=r'^[A-D]$')
    consequences: Optional[str] = None
    to_node_id: Optional[int] = None

class ChoiceResponse(ChoiceBase):
    choice_id: int
    from_node_id: int
    to_node_id: int
    
    class Config:
        from_attributes = True
