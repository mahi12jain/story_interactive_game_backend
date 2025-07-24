# GET /api/stories/search?q={query}   # Search stories

from fastapi import APIRouter,Depends,HTTPException,status,Query
from app.database import get_db,get_async_db
from app.models.story import Story,StoryNode
from app.schemas.story_schemas import StoryBase,StoryCreate,StoryListResponse,StoryResponse,StoryUpdate,CategoriesListResponse
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func, distinct
from typing import List,Optional


router = APIRouter(prefix="/story", tags=["Stories"])


@router.post('/stories', response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
def create_story(
    story_data: StoryCreate,
    db: Session = Depends(get_db)
):
    story_title = db.query(Story).filter(Story.title == story_data.title).all()

    if story_title:
        raise HTTPException(status_code=400,detail="story all ready exit")
    
    db_add = Story(
        title = story_data.title,
        description = story_data.description,
        author = story_data.author,
        difficulty_level = story_data.difficulty_level,
        category = story_data.category,
        is_published = story_data.is_published,
        created_at = story_data.created_at
    )

    db.add(db_add)
    db.commit()
    db.refresh(db_add)

    return db_add

# get story
@router.get('/get_story', response_model = List[StoryResponse])
def get_story(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        categorys = db.query(Story).offset(skip).limit(limit).all()
        return categorys
    except:
        raise HTTPException(status = status.HTTP_401_UNAUTHORIZED,
                            detail="U hve not uthrization")
    
@router.get('/get_story/{story_id}', response_model = StoryResponse)
def get_story_id(story_id,db:Session = Depends(get_db)):
    story_getid = db.query(Story).filter(Story.story_id == story_id).first()

    if not story_getid:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="ID not found pls write the correct id")
    
    return story_getid

@router.put('/stories/{story_id}', response_model=StoryResponse)
def update_story(
    story_id: int,
    story_data: StoryUpdate,
    db: Session = Depends(get_db)
):
    """Update existing story"""
    story = db.query(Story).filter(Story.story_id == story_id).first()
    
    if not story:
        raise HTTPException(
            status_code=404,
            detail="Story not found"
        )
    
    # Update only provided fields
    update_data = story_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(story, field, value)
    
    try:
        db.commit()
        db.refresh(story)
        return story
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update story: {str(e)}"
        )

@router.delete('/stories/{story_id}', response_model=StoryResponse)
def detele_storyid(story_id,db:Session= Depends(get_db)):
    find_story = db.query(Story).filter(Story.story_id == story_id).first()

    db.delete(find_story)
    db.commit()

    return JSONResponse(
        status_code=200,
        content={"message": f"User with ID {find_story.title} has been deleted successfully"}
    )

@router.get('/stories/categories', response_model=CategoriesListResponse)
def get_story_categories(
    db: Session = Depends(get_db),
    published_only: bool = Query(True, description="Only include categories from published stories")
):
    """
    Get all unique story categories
    Simple list of category names
    """
    try:
        query = db.query(distinct(Story.category)).filter(Story.category.isnot(None))
        
        if published_only:
            query = query.filter(Story.is_published == True)
        
        categories = query.all()
        
        # Extract category names from tuples
        category_names = [cat[0] for cat in categories if cat[0]]
        
        return CategoriesListResponse(
            categories=sorted(category_names),
            total_count=len(category_names)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {str(e)}"
        )

# @router.get('stories/search?q={query}',response_model=)