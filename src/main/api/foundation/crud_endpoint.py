


from typing import Optional, Protocol


class CrudEndpoint(Protocol):
    def post(self, model: Optional[BaseModel]) -> BaseModel | Response:...
    def get(self, user_id: int) -> BaseModel | Response:...
    def delete(self, user_id: int) -> BaseModel | Response:...
    
        