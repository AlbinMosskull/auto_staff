from pydantic import BaseModel
from typing import Union
import backend

# TODO: Incorporate this in the interface to frontend

class BackendTicketResponse(BaseModel):
	ticket_type: str
	traveler_type: str
	price: float

class BackendRouteResponse(BaseModel):
	movement_message: str

class BackendQuestionResponse(BaseModel):
	question: str

class BackendResponse(BaseModel):
	response: Union[BackendTicketResponse,
				 	BackendRouteResponse,
					BackendQuestionResponse]

