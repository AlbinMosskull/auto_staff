import openai
from enum import Enum
from pydantic import BaseModel
from typing import Union

from tickets import (
	parse_ticket_info,
	get_ticket_types,
	get_traveler_types,
)
from route_planning import (
	manage_route_planning_request,
)

class QuestionResponse(BaseModel):
	question: str

class TicketResponse(BaseModel):
	ticket_type: str
	traveler_type: str

class DestinationResponse(BaseModel):
	destination: str

class ResponseType(Enum):
	ROUTE_PLANNING = "route_planning"
	TICKET_PURCHASE = "ticket_purchase"
	ADDITIONAL_QUESTION = "additional_question"

class ResponseMessage(BaseModel):
	response_type: ResponseType
	sub_response: Union[TicketResponse, DestinationResponse, QuestionResponse]




def create_gpt3_client(api_key):
	return openai.OpenAI(api_key=api_key)



def manage_incoming_message(message_history, client, model, origin_id, sl_api_key):
	system_messages = [
				{"role": "system", "content": "You are Metro Auto-Staff, an assistant helping travelers in the Stockholm metro."},
				{"role": "system", "content": "You have two tasks that you help with. Navigating to a certain station, or selling tickets to users."},
				{"role": "system", "content": "If you do not have enough context to help with these tasks, you ask a question to learn more."},
				{"role": "system", "content": "You are polite, but does not engage in small talk beyond your task."},

				# Task 1: Route Planning
				{"role": "system", "content": "If the user is asking about how to go somewhere, then you want to determine their desired destination."},
				{"role": "system", "content": "Your task is to parse the name of a station in the Stockholm metro from the user prompt."},
				{"role": "system", "content": "Example: I would like to go to Näckrosen. Then the correct output is 'Näckrosen'."},

				# Task 2: Ticket Purchase
				{"role": "system", "content": "If the user asks about buying a ticket, your task is to parse the ticket type and traveler type from a user prompt."},
				{"role": "system", "content": "However, if that information cannot be parsed, ask a question instead."},
				{"role": "system", "content": "Example: I would like to buy a single ticket, I am a student. Then the correct output is 'single', 'student'."},
				{"role": "system", "content": "Available ticket types: " + str(get_ticket_types())},
				{"role": "system", "content": "Available traveler types: " + str(get_traveler_types())},
				{"role": "system", "content": "If the user has not told you which traveler type they are, you need to ask them about it by asking an additional_question."},

				# Task 3: Additional Question
				{"role": "system", "content": "If the user does not provide enough information, you ask a question to learn more."},
				{"role": "system", "content": "Example: I would like to buy a single ticket. Then you should ask about which of the traveler types they are."},
				{"role": "system", "content": "Make absolutely sure you know everything you need by asking questions before you do one of the tasks above."},
				{"role": "system", "content": "Only ask about information not yet provided."},
				{"role": "system", "content": "Set the response type to 'additional_question'."},
			]
	
	response = client.beta.chat.completions.parse(
		model=model,
		messages= system_messages + message_history,
		response_format=ResponseMessage
	)

	parsed_message = response.choices[0].message.parsed
	if not parsed_message:
		print("ERROR: Failed to parse response.")
		return "Parsing failed."

	message_type = parsed_message.response_type.value
	message_content = parsed_message.sub_response
		
	print("message_type:", message_type)
	print("message_content:", message_content)

	if message_type == ResponseType.ROUTE_PLANNING.value:
		print("INFO:", "Route planning request")
		destination_name = message_content.destination
		route_info = manage_route_planning_request(destination_name, origin_id, sl_api_key)
		return route_info

	elif message_type == ResponseType.TICKET_PURCHASE.value:
		print("INFO:", "Ticket purchase request")
		ticket_type = message_content.ticket_type
		traveler_type = message_content.traveler_type

		ticket_info = parse_ticket_info(ticket_type, traveler_type)
		return ticket_info
	
	elif message_type == ResponseType.ADDITIONAL_QUESTION.value:
		print("INFO:", "Additional question request")
		question = message_content.question

		return question
		
	
	else:
		return "Unknown request type."



class AutoStaffModel:
	"""
	This class receives the user input.

	It stores the user input and uses it to determine which action to take.

	It returns the response that is to be communicated to the user.
	"""

	def __init__(self, client, model, station_id, sl_api_key):
		self.client = client
		self.model = model
		self.station_id = station_id
		self.sl_api_key = sl_api_key
		self._received_messages = []

	def add_message(self, message, role="user"):
		self._received_messages.append(
			{"role": role, "content": message}
		)

	def produce_response(self):
		"""
		Decide upon an action to take based on the history of the conversation.
		"""
		response = manage_incoming_message(
			self._received_messages,
			self.client,
			self.model,
			self.station_id,
			self.sl_api_key
		)
		self.add_message(response, role="assistant")
		return response


def create_auto_staff_model_default_settings():
	f = open('./apikey.txt', 'r', encoding='utf-8')
	CHATGPT_API_KEY = f.readlines()[0]
	GPT_MODEL = "gpt-4o-mini"
	client = create_gpt3_client(CHATGPT_API_KEY)
	CURRENT_STATION_ID = "300109001"  # T-Centralen
	SL_API_KEY = "TRAFIKLAB-SLAPI-INTEGRATION-2024"
	return AutoStaffModel(client, GPT_MODEL, CURRENT_STATION_ID, SL_API_KEY)



def main():
	auto_staff_model = create_auto_staff_model_default_settings()

	while True:
		user_input = input("User: ")
		auto_staff_model.add_message(user_input)
		response = auto_staff_model.produce_response()
		print(f"Assistant: {response}")


if __name__ == "__main__":
    main()




