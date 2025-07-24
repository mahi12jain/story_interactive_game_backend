from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.choice import Choice
from app.models.story import StoryNode
from app.schemas.choice_schemas import (
    ChoiceCreate, ChoiceUpdate, ChoiceResponse
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/choices", tags=["Choices"])

@router.post("/", response_model=ChoiceResponse, status_code=status.HTTP_201_CREATED)
def create_choice(
    choice_data:ChoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new choice between story nodes"""
    from_node = db.query(StoryNode).filter(StoryNode.node_id == choice_data.from_node_id).first()
    to_node = db.query(StoryNode).filter(StoryNode.node_id == choice_data.to_node_id).first()

    if not from_node:
        raise HTTPException(
            status_code=404,
            detail="Source node not found"
        )
    
    if not to_node:
        raise HTTPException(
            status_code=404,
            detail="Destination node not found"
        )
       
    # Verify both nodes belong to the same story
    if from_node.story_id != to_node.story_id:
        raise HTTPException(
            status_code=400,
            detail="Both nodes must belong to the same story"
        )

    # Check if choice letter is already used for this node
    existing_choice = db.query(Choice).filter(Choice.from_node_id == choice_data.from_node_id,
                                              Choice.choice_letter == choice_data.choice_letter).first()
    
    if existing_choice:
        raise HTTPException(
            status_code = 400,
            detail=f"Choice letter '{choice_data.choice_letter}' already exists for this node"
        )
    
    # Prevent choices from ending nodes
    if from_node.is_ending_node:
        raise HTTPException(
            status_code = 400,
            detail = "Cannot create  choices from ending nodes"
        )

    db_choice = Choice(
        from_node_id=choice_data.from_node_id,
        to_node_id=choice_data.to_node_id,
        choice_text=choice_data.choice_text,
        choice_letter=choice_data.choice_letter,
        consequences=choice_data.consequences
    )
    
    db.add(db_choice)
    db.commit()
    db.refresh(db_choice)
    
    return db_choice

@router.get("/node/{node_id}", response_model=List[ChoiceResponse])
def get_node_choices(
    node_id :int,
    db: Session = Depends(get_db)
):
    node = db.query(StoryNode).filter(StoryNode.node_id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=404,
            detail = "Story not found"
        )
    
    choices = db.query(Choice).filter(Choice.from_node_id == node_id).order_by(Choice.choice_letter).all()

    return choices

@router.get("/{choice_id}", response_model=ChoiceResponse)
def get_choice(
    choice_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific choice by ID"""
    choice = db.query(Choice).filter(Choice.choice_id == choice_id).first()
    if not choice:
        raise HTTPException(
            status_code=404,
            detail="Choice not found"
        )
    
    return choice

@router.put("/{choice_id}", response_model=ChoiceResponse)
def update_choice(
    choice_id: int,
    choice_data: ChoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing choice"""
    choice = db.query(Choice).filter(Choice.choice_id == choice_id).first()
    if not choice:
        raise HTTPException(
            status_code=404,
            detail="Choice not found"
        )
    
    # If updating choice letter, check for conflicts
    if choice_data.choice_letter and choice_data.choice_letter != choice.choice_letter:
        existing_choice = db.query(Choice).filter(
            Choice.from_node_id == choice.from_node_id,
            Choice.choice_letter == choice_data.choice_letter,
            Choice.choice_id != choice_id
        ).first()
        
        if existing_choice:
            raise HTTPException(
                status_code=400,
                detail=f"Choice letter '{choice_data.choice_letter}' already exists for this node"
            )
    
    # If updating destination node, verify it exists and belongs to same story
    if choice_data.to_node_id and choice_data.to_node_id != choice.to_node_id:
        new_to_node = db.query(StoryNode).filter(
            StoryNode.node_id == choice_data.to_node_id
        ).first()
        
        if not new_to_node:
            raise HTTPException(
                status_code=404,
                detail="New destination node not found"
            )
        
        # Verify same story
        from_node = db.query(StoryNode).filter(
            StoryNode.node_id == choice.from_node_id
        ).first()
        
        if new_to_node.story_id != from_node.story_id:
            raise HTTPException(
                status_code=400,
                detail="Destination node must belong to the same story"
            )
    
    # Update only provided fields
    update_data = choice_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(choice, field, value)
    
    try:
        db.commit()
        db.refresh(choice)
        return choice
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update choice: {str(e)}"
        )

@router.delete("/{choice_id}")
def delete_choice(
    choice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a choice"""
    choice = db.query(Choice).filter(Choice.choice_id == choice_id).first()
    if not choice:
        raise HTTPException(
            status_code=404,
            detail="Choice not found"
        )
    
    try:
        db.delete(choice)
        db.commit()
        return {"message": f"Choice '{choice.choice_text}' deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete choice: {str(e)}"
        )

@router.get("/story/{story_id}/all", response_model=List[ChoiceResponse])
def get_all_story_choices(
    story_id: int,
    db: Session = Depends(get_db)
):
    """Get all choices for a specific story"""
    choices = db.query(Choice).join(StoryNode, Choice.from_node_id == StoryNode.node_id).filter(
        StoryNode.story_id == story_id
    ).order_by(Choice.from_node_id, Choice.choice_letter).all()
    
    return choices