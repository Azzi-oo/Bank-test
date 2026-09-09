from pydantic import BaseModel, Field

from src.main.api.models.user import UserIdentity


class LoginResponse(BaseModel):
    token: str = Field(min_length=1)
    user: UserIdentity
