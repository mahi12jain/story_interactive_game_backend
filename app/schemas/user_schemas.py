from pydantic import BaseModel, Field,EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50,description="Unique username for the user")
    email: EmailStr = Field(..., description="User's valid email address.")
    password: str = Field(..., min_length=8, description="User's plain-text password. Will be hashed before saving.")
    
class Userlogin(BaseModel):
    email: EmailStr = Field(..., description="User's valid email address.")
    password: str = Field(..., min_length=8, description="User's plain-text password.")
    

# 2. Schemas for API Responses (Controlling what data is sent back)
class UserBase(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    
    class config:
        orm_mode = True
    
class UserPublic(UserBase):
    created_at: datetime
    last_active: datetime

class UserStatsPublic(BaseModel):
    stories_completed: int
    total_choices_made: int
    favorite_category: str
    total_play_time: int
    
    class config:
        orm_mode = True

class UserProfile(UserPublic):
    stats: Optional[UserStatsPublic] = None

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None

# 3. Schemas for Token Data (Standardizing JWT and API tokens)
class Token(BaseModel):
    access_token: str
    refresh_token:  Optional[str] = None 
    
class TokenData(BaseModel):
    id: Optional[int] = None
    
