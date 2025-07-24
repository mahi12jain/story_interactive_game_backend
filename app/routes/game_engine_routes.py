from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.game_engine_service import GameEngine
from app.schemas.engine_schemas import (
    NodeResponse, ChoiceRequest, ChoiceResponse, ValidationResult
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/game", tags=["Game Engine"])

@router.post("/start/{story_id}", response_model=NodeResponse)
def start_storys(
    story_id:int,
    db:Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)):
    """Start a new story session"""
    engine = GameEngine(db)
    user_id = current_user.user_id if current_user else None

    return engine.start_story(story_id,user_id)

@router.post("/choice", response_model=ChoiceResponse)
def make_choice(
    choice_request : ChoiceRequest,
    db: Session = Depends(get_db),
    current_user : Optional[User] = Depends(get_current_user)
):
    """Make choice to get a next node"""
    engine = GameEngine(db)
    # If user is authenticated, use their ID; otherwise use the one from request
    if current_user:
        choice_request.user_id = current_user.user_id

    return engine.make_choice(choice_request) 

@router.get("/current/{story_id}", response_model=NodeResponse)
def get_current_node(
    story_id :int,
    db:Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    """Get the current node for authenticated user's story progress"""
    engine = GameEngine(db)
    return engine.get_current_node(story_id,current_user.user_id)





