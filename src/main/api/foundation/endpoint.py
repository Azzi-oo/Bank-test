from requests import request
from src.main.api.models.requests import BaseModel, CreateUserRequest


from typing import Optional, Type


class EndpointConfiguration:
    url: str
    request_model: Optional[Type[BaseModel]]
    response_model: Optional[Type[BaseModel]]
    

class Endpoint:
    ADMIN_CREATE_USER = EndpointConfiguration(
        request_model = CreateUserRequest,
        url="/admin/create",
        response_model=CreateUserResponse
    )