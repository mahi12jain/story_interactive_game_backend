from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext 
from sqlalchemy.orm import Session

from app.models import user as user_model
from app.schemas.user_schemas import UserCreate
from app.database import get_db # Your DB session dependency
from config import settings # Import settings from your config file

# password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

# password Utility Functions
def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 4. Core Authentication and User Functions
def get_user_email(db: Session, email: str) -> Optional[user_model.User]:
    return db.query(user_model.User).filter(user_model.User.email == email).first()

def create_user(db: Session, user_data: UserCreate) -> user_model.User:
    password_hash = get_password_hash(user_data.password)
    db_user = user_model.User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[user_model.User]:
    """
    Authenticates a user.
    - Fetches the user by email.
    - Verifies the provided password against the stored hash.
    - Returns the user object on success, otherwise None.
    """
    user = get_user_email(db, email)
    if not user:
        return None
    # Safely get the password_hash value
    password_hash = getattr(user, "password_hash", None)
    if not isinstance(password_hash, str):
        return None
    if not verify_password(password, password_hash):
        return None
    return user

# 5. JWT Handling Functions


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    
    # Use getattr with a default value if the setting is missing
    expire_minutes = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 30)
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt



# 6. Protected Route Dependency
def get_current_user(
    token: str = Depends(oauth2),
    db: Session = Depends(get_db)
) -> user_model.User:
    """
    A dependency to be used in protected routes.
    
    - Decodes the JWT from the request's Authorization header.
    - Validates the token and extracts the user ID.
    - Fetches the user from the database.
    - Raises HTTPException if the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception
    user = db.query(user_model.User).filter(user_model.User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    return user