from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.auth.models import AuthenticatedUser
from app.auth.service import auth_service
from app.common.exceptions import AccountLockedError, AuthenticationError, ValidationError
from app.server.dependencies import get_admin_user, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1)
    new_password: str = Field(min_length=1)


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str = "user"
    must_change_password: bool = True


@router.post("/login")
def login(payload: LoginRequest, request: Request) -> dict:
    try:
        result = auth_service.login(payload.username, payload.password, headers=dict(request.headers))
        return {
            "token": result.session_token,
            "must_change_password": result.must_change_password,
            "user": {
                "id": result.user.id,
                "username": result.user.username,
                "role": result.user.role,
            },
        }
    except AccountLockedError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(exc)) from exc
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout")
def logout(
    user: AuthenticatedUser = Depends(get_current_user),
    authorization: str | None = Header(default=None),
    x_session_token: str | None = Header(default=None),
) -> dict:
    token = x_session_token or (authorization[7:].strip() if authorization and authorization.lower().startswith("bearer ") else None)
    auth_service.logout(token, username=user.username)
    return {"status": "ok"}


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    try:
        auth_service.change_password(user, payload.old_password, payload.new_password)
        return {"status": "ok"}
    except (AuthenticationError, ValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/users")
def create_user(payload: CreateUserRequest, admin: AuthenticatedUser = Depends(get_admin_user)) -> dict:
    try:
        user = auth_service.create_user(payload.username, payload.password, payload.role, payload.must_change_password)
        return {"id": user.id, "username": user.username, "role": user.role, "created_by": admin.username}
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/me")
def me(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    return {"id": user.id, "username": user.username, "role": user.role, "must_change_password": user.must_change_password}
