


from pydantic import BaseModel
from main.api.foundation.http_requester import HttpRequester
from main.api.foundation.requesters.crud_requester import CrudRequester


class ValidateCrudRequester(HttpRequester):
    def __init__(self, request_spec, endpoint, response_spec):
        super().__init__(request_spec, endpoint, response_spec)
        self.crud_requester = CrudRequester(
            request_spec=request_spec,
            endpoint=endpoint,
            response=response_spec
        )
        
    def post(self, model: BaseModel) -> BaseModel:
        response = self.crud_requester.post(model)
        self.response_spec(response)
        return self.endpoint.value.response_model.model_validate(response.json())
    
    def delete(self, user_id: int):
        response = self.crud_requester.delete(user_id)
        self.response_spec(response)
        return self.endpoint.value.response_model.model_validate(response.json())