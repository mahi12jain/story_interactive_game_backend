from sqlalchemy import Column, Integer, String, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func

class Choice(Base):
    __tablename__ = 'choices'

    choice_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    from_node_id = Column(Integer, ForeignKey('story_nodes.node_id'), nullable=False)  # Fixed: Use table name
    to_node_id = Column(Integer, ForeignKey('story_nodes.node_id'), nullable=False)    # Fixed: Use table name
    choice_text = Column(String(500), nullable=False)  # "Option A: Go left"
    choice_letter = Column(String(1), nullable=False)  # 'A', 'B', 'C', 'D'
    consequences = Column(Text, nullable=True)  # Optional flavor text
    
    # Relationships
    from_node = relationship("StoryNode", foreign_keys=[from_node_id], back_populates="choices_from")
    to_node = relationship("StoryNode", foreign_keys=[to_node_id], back_populates="choices_to")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("choice_letter IN ('A', 'B', 'C', 'D')", name='valid_choice_letter'),
    )