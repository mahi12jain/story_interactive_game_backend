from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db, get_async_db  # Import both sync and async
from app.models.user import User
from app.schemas.user_schemas import UserCreate, Userlogin, Token, TokenData, UserPublic, UserProfile
from app.services.auth_service import authenticate_user, create_access_token, get_current_user, create_user, get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  # Fixed tokenUrl

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    # Use async syntax with select()
    result = await db.execute(select(User).filter(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    # Create new user with proper password hashing
    db_user = User(
        username=user.username,  # Make sure this field exists in UserCreate
        email=user.email,
        password_hash=get_password_hash(user.password)  # Properly hash the password
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token, summary="Log in to get access token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)  # Keep this as sync for now
):
    user = authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a JWT token
    access_token = create_access_token(
        data={"user_id": user.user_id}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user's profile"
)
async def read_users_me(
    current_user: User = Depends(get_current_user)  # Changed from UserPublic to User
):
    """
    A protected endpoint to fetch the current authenticated user's profile.

    - The `get_current_user` dependency handles all the token validation.
    - If the token is invalid or expired, the dependency will raise an HTTPException.
    - If the token is valid, the user's data is returned.
    """
    return current_user