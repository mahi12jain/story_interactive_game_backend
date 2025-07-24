from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, DateTime,JSON,Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"  # Use lowercase, plural table names

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Match your schema
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_active = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    stats = relationship("UserStats", back_populates="user", uselist=False)
    progress = relationship("UserProgress", back_populates="user")

     
class UserStats(Base):
    __tablename__ = "stats"

    stat_id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    stories_completed = Column(Integer, default=0)
    total_choices_made = Column(Integer, default=0)
    favorite_category = Column(String(255), default="")
    total_play_time = Column(Integer, default=0) # in minutes
    user = relationship("User", back_populates="stats")
    

