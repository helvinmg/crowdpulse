"""Authentication routes: signup, login, current user."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User
from app.models.user_config import UserConfig

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    name: str | None
    onboarding_complete: bool


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/signup", response_model=AuthResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=req.email.lower().strip(),
        hashed_password=hash_password(req.password),
        name=req.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create default config
    config = UserConfig(user_id=user.id, use_defaults=True)
    db.add(config)
    db.commit()

    token = create_access_token(user.id, user.email)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "onboarding_complete": user.onboarding_complete,
        },
    }


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token(user.id, user.email)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "onboarding_complete": user.onboarding_complete,
        },
    }


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """Return the current authenticated user."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "onboarding_complete": user.onboarding_complete,
    }
