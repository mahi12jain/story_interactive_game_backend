from sqlalchemy import  Column, Integer, String, DateTime,Boolean,ForeignKey,Enum,Text
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func
import enum



class Story(Base):
    __tablename__ = "stories"

    story_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)  # Use Text for longer descriptions
    author = Column(String(100), nullable=False, index=True)
    difficulty_level = Column(String(20), default="easy", nullable=False)  # Use string
    category = Column(String(50), nullable=True, index=True)  # Add index for filtering
    is_published = Column(Boolean, default=False, nullable=False)  # Default to False for safety
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    nodes = relationship("StoryNode", back_populates="story", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="story")  # Changed from user_progress to progress

class StoryNode(Base):
    __tablename__ = "story_nodes"

    node_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    story_id = Column(Integer, ForeignKey('stories.story_id'), nullable=False)
    node_title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # Use Text for story content
    is_starting_node = Column(Boolean, default=False, nullable=False)
    is_ending_node = Column(Boolean, default=False, nullable=False)
    node_type = Column(String(50), nullable=False, index=True)
    
    # Relationships
    story = relationship("Story", back_populates="nodes")
    choices_from = relationship("Choice", foreign_keys="Choice.from_node_id", back_populates="from_node")
    choices_to = relationship("Choice", foreign_keys="Choice.to_node_id", back_populates="to_node")

