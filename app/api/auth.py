from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models.user import Token, User, UserCreate, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


def _get_user_session():
    """Convenience: get a fresh DB session bound to the shared engine."""
    from app.services.ingestion import get_engine

    engine = get_engine()
    return User._session(engine)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(payload: UserCreate) -> UserResponse:
    session = _get_user_session()
    try:
        existing = session.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info("Registered user '%s' (admin=%s)", user.email, user.is_admin)
        return UserResponse.model_validate(user)
    finally:
        session.close()


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and receive a JWT access token",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    session = _get_user_session()
    try:
        user = (
            session.query(User)
            .filter(User.email == form_data.username)
            .first()
        )
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        token = create_access_token(data={"sub": user.email})
        return Token(access_token=token)
    finally:
        session.close()
