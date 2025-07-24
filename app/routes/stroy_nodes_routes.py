from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.story import StoryNode, Story
from app.models.choice import Choice
from app.schemas.story_nodes_shcemas import (
    StoryNodeCreate, StoryNodeUpdate, StoryNodeResponse
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/story_nodes",tags=["Story Nodes"])

@router.post("/",response_model=StoryNodeResponse,status_code=status.HTTP_201_CREATED)
def create_story_node(
    node_data : StoryNodeCreate,
    db: Session = Depends(get_db),
    current_user = get_current_user
):
    story = db.query(Story).filter(Story.story_id == node_data.story_id).first()

    if not story:
        raise HTTPException(
            status_code=404,
            detail="Stroy Not Found"
        )

    # Check if this is going to be a starting node
    if node_data.is_starting_node:
        existing_start = db.query(StoryNode).filter(StoryNode.story_id == node_data.story_id,StoryNode.is_starting_node == True).first()

        if existing_start:
            raise HTTPException(status_code=400,detail="Story already has a starting Node")
        
    
    db_node = StoryNode(
        story_id=node_data.story_id,
        node_title=node_data.node_title,
        content=node_data.content,
        is_starting_node=node_data.is_starting_node,
        is_ending_node=node_data.is_ending_node,
        node_type=node_data.node_type
    )
    
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    
    return db_node


@router.get("/story/{story_id}", response_model=List[StoryNodeResponse])
def get_story_nodes(
    story_id:int,skip:int = 0, limit:int = 100,db: Session = Depends(get_db)
):
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException (status_code=404,detail="Stroy Not found")
    
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story_id).offset(skip).limit(limit).all()

    return nodes

@router.get("/{node_id}", response_model=StoryNodeResponse)
def get_story_node(
    node_id : int,
    node_data : StoryNodeUpdate,
    db : Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing story node"""
    node = db.query(StoryNode).filter(StoryNode.node_id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=404,
            detail = "Stroy node not found"
        )
    
    # If updating to be starting node, ensure no other starting node exists
    if node_data.is_starting_node not in node.is_starting_node:
        existing_start = db.query(StoryNode).filter(
            StoryNode.story_id == node.story_id,
            StoryNode.is_starting_node == True,
            StoryNode.node_id != node_id
        ).first()

        if existing_start:
            raise HTTPException(
                status_code= 400,
                detail = "Story already starting node"
            )
    # update only provided fields
    update_data = node_data.dict(exclude_unset=True)
    for field,value in update_data.items():
        setattr(node,field,value)

    try:
        db.commit()
        db.refresh(node)
        return node
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code = 500,
            detail = f"Failed to update story node: {str(e)}"
        )
    
@router.delete("{node_id}")
def delete_story_node(
    node_id:int,db:Session = Depends(get_db),current_user = Depends(get_current_user)
):
    node = db.query(StoryNode).filter(StoryNode.node_id == node_id).first()
    if not node:
        raise HTTPException(
            status_code= 404,
            detail="Story Node not found"
        )

    # Check if this node has choices pointing to it or from it
    incoming_choices = db.query(Choice).filter(Choice.to_node_id == node_id).count()
    outgoing_choices = db.query(Choice).filter(Choice.from_node_id == node_id).count()

    if incoming_choices > 0 or outgoing_choices > 0:
        raise HTTPException(
            status_code=400,
            detail= "Cannot delete node with existing choices.Remove choice first"
        )
    
    try:
        db.delete(node)
        db.commit()
        return {"message": f"Story node '{node.node_title}' deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete story node: {str(e)}"
        )
    
@router.get("/story/{story_id}/starting-node", response_model=StoryNodeResponse)
def get_starting_node(
    story_id :int,
    db : Session = Depends(get_db)
):
    """Get the starting node for a story"""
    starting_node = db.query(StoryNode).filter(
        StoryNode.story_id == story_id,
        StoryNode.is_starting_node == True
    ).first()

    if not starting_node:
        raise HTTPException(
            status_code = 404,
            detail="Starting node not found for this story"
        )
    
    return starting_node
