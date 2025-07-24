from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, DateTime,JSON,Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func


class UserProgress(Base):
    __tablename__ = "user_progress"

    progress_id = Column(Integer,primary_key=True,autoincrement=True,index=True)
    user_id = Column(Integer,ForeignKey('users.user_id'))
    story_id = Column(Integer,ForeignKey("stories.story_id"))
    current_node_id = Column(Integer,ForeignKey('story_nodes.node_id'))
    choice_node = Column(JSON,nullable=True)
    start_time =  Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    is_completed = Column(Boolean,default=False)

    user = relationship("User", back_populates="progress")
    story = relationship("Story",back_populates="progress")
