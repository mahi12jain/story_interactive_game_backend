from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# class DifficultyLevel(str, Enum):
#     EASY = "easy"
#     MEDIUM = "medium"
#     HARD = "hard"


class StoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    author: str = Field(..., min_length=1, max_length=100)
    difficulty_level: str = "easy"  # Change to string for simplicity
    category: Optional[str] = Field(None, max_length=50)
    is_published: bool = False
    created_at : datetime

class StoryCreate(StoryBase): 
    pass

class StoryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    difficulty_level: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    is_published: Optional[bool] = None

class StoryResponse(StoryBase):
    story_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StoryListResponse(BaseModel):
    story_id: int
    title: str
    author: str
    difficulty_level: str
    category: Optional[str]
    is_published: bool
    created_at: datetime
    total : int
    skip : int
    limit : int
    
    class Config:
        from_attributes = True

# Response schemas for categories
class CategoryResponse(BaseModel):
    """Single category with count"""
    name: str
    count: int

class CategoriesListResponse(BaseModel):
    """List of all categories"""
    categories: List[str]
    total_count: int

class CategoriesWithCountResponse(BaseModel):
    """Categories with story counts"""
    categories: List[CategoryResponse]
    total_categories: int