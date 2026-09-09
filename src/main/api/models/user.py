from pydantic import BaseModel, Field

from src.main.api.models.requests import UserRole


class UserIdentity(BaseModel):
    username: str
    role: UserRole


class CreateUserResponse(UserIdentity):
    id: int = Field(gt=0)
