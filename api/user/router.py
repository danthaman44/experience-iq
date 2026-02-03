"""
User router for handling user registration and management.
"""

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from api.core.schemas import User
from api.db.service import create_or_update_user
from api.core.dependencies import SupabaseClient


router = APIRouter(prefix="/api/users", tags=["users"])


class UserRegisterRequest(BaseModel):
    """Request model for user registration."""

    id: str
    displayName: str | None = None
    primaryEmail: str | None = None
    primaryEmailVerified: bool = False
    profileImageUrl: str | None = None


class UserRegisterResponse(BaseModel):
    """Response model for user registration."""

    status: str
    message: str
    user_id: str


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_200_OK,
)
async def register_user(
    supabase: SupabaseClient, http_request: Request, request: UserRegisterRequest
) -> UserRegisterResponse:
    """
    Register a new user.

    Args:
        http_request: FastAPI request object
        request: User registration request with user details

    Returns:
        UserRegisterResponse: Registration success response
    """
    user = User(
        id=request.id,
        displayName=request.displayName,
        primaryEmail=request.primaryEmail,
        primaryEmailVerified=request.primaryEmailVerified,
        profileImageUrl=request.profileImageUrl,
    )
    try:
        data = create_or_update_user(supabase, user)
        if data:
            return UserRegisterResponse(
                status="success",
                message="User registered successfully",
                user_id=request.id,
            )
        else:
            return UserRegisterResponse(
                status="error",
                message="Failed to create or update user",
                user_id=request.id,
            )
    except Exception as e:
        return UserRegisterResponse(
            status="error",
            message=f"Error creating or updating user: {e}",
            user_id=request.id,
        )
