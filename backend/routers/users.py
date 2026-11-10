
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas import UserRegister, UserOut, Token
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/register", response_model=UserOut)
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(
        User.username == data.username
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )

    new_user = User(
        username=data.username,
        password=hash_password(data.password),
        role="author"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password, user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    token = create_access_token({
        "sub": user.username
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserOut)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
