from pydantic import BaseModel
from typing import Optional
import uuid


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None


from app.schemas.user import UserResponse
Token.model_rebuild()

