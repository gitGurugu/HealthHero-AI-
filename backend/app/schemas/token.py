from typing import Optional

from pydantic import BaseModel
from .user import UserOut


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut 