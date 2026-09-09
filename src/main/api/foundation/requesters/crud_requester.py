
import requests

from typing import Optional
from requests import Response
from pydantic import BaseModel
from main.api.foundation.endpoint import EndpointConfiguration
from main.api.foundation.http_requester import HttpRequester


class CrudRequester(HttpRequester):
    def post(self, model: Optional[BaseModel]) -> BaseModel | Response:
        body = model.model_dump() if model is not None else ""
        
        response = requests.post(
            url=f"{Config.fetch("backendUrl")}{self.endpoint.value.url}",
            headers=self.request_spec,
            json=body
        )
        self.response_spec(response)
        return response
    
    def delete(self, user_id: int) -> BaseModel | Response:
        response = requests.delete(
            url="/admin/create",
            headers=self.request_spec
        )
        self.response_spec(response)
        return response
        
       