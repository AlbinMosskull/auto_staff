import requests
import openai
from pydantic import BaseModel


class StationResponse(BaseModel):
    station_name: str


def create_gpt3_client(api_key):
	return openai.OpenAI(api_key=api_key)


def parse_destination(prompt, client, model):
	messages = [{"role": "system", "content": "Your task is to parse the name of a station in the Stockholm metro from a user prompt."},
				{"role": "system", "content": "Example: I would like to go to Näckrosen. Then the correct output is 'Näckrosen'."}]

	response = client.beta.chat.completions.parse(
	model=model,
	messages= messages + 
		[{"role": "user", "content": prompt}],
	response_format=StationResponse
	)

	if response.choices[0].message.parsed:
		assert isinstance(response.choices[0].message.parsed, StationResponse), "Unexpected response type."
		return response.choices[0].message.parsed.station_name
	else:
		return None


def lookup_station_id(station_name, api_key):
	"""
	Fetches the SiteId of a stop based on the provided destination name.

	:param destination_name: The name of the destination (max 20 characters).
	:return: A list of stops with SiteId, Name, and Type, or an error message string.
	"""
	base_url = "https://journeyplanner.integration.sl.se/v1/typeahead.json"
	params = {
		"key": api_key,
		"searchstring": station_name,
		"stationsonly": "true",
		"maxresults": 5
	}

	try:
		response = requests.get(base_url, params=params)
		response.raise_for_status()
		data = response.json()
		
		if data["StatusCode"] != 0:
			return f"Error: {data['Message']}"
		
		stops = data.get("ResponseData", [])
		
		if not stops:
			return "No stops found."
		
		return [{"Name": stop["Name"], "SiteId": stop["SiteId"], "Type": stop["Type"]} for stop in stops]

	except requests.RequestException as e:
		return f"Request failed: {e}"


def get_route(origin_id, dest_id, api_key):
    """
    Get route suggestions between two stations using SL's Route Planner API
    
    Args:
        origin_id (str): Starting station ID (9 digits, e.g., '300109001')
        dest_id (str): Destination station ID (9 digits, e.g., '300109001')
        api_key (str): Your API key for the SL Route Planner
    """
    base_url = "https://journeyplanner.integration.sl.se/v1/TravelplannerV3_1/trip.json"
    
    params = {
        'key': api_key,
        'originExtId': origin_id,
        'destExtId': dest_id,
        'lang': 'en'  # Response language (en/sv/de)
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error making request: {e}"


def parse_duration(duration):
	return duration[2:-1]


def create_response_route_info_message(route_info):
	if not 'Trip' in route_info:
		return "No trips found for the given stations."

	# Get the first trip only
	response_message = ""
	trip = route_info['Trip'][0]
	leg_list = trip.get('LegList', {}).get('Leg', [])
	if leg_list:
		duration = parse_duration(trip.get('duration'))
		print("\nTrip details:")
		for leg in leg_list:
			transport = leg.get('Product', {}).get('name', 'Walking')
			origin = leg['Origin']['name']
			destination = leg['Destination']['name']
			response_message += f"Take the {transport} from {origin} to {destination}\n"
			print(f"Take the {transport} from {origin} to {destination}")
		response_message += f"Total duration: {duration} minutes"
		print(f"Total duration: {duration} minutes")
		return response_message
	else:
		return "No trip details found."



def manage_incoming_message(message, client, model, origin_id, sl_api_key):
	# Currently we always assume the request is a route planning request
	destination_name = parse_destination(message, client, model)
	if not destination_name:
		print("Sorry, I couldn't understand the destination you provided. Please try again.")
		return
	
	print("INFO:", f"Destination station: {destination_name}")
	
	destination_id_infos = lookup_station_id(destination_name, sl_api_key)
	if isinstance(destination_id_infos, str):
		print(destination_id_infos)
		return
	
	destination_id_info = destination_id_infos[0]
	print("INFO:", f"Destination station ID: {destination_id_info['SiteId']}")
	
	destination_id = destination_id_info["SiteId"]

	route_info = get_route(origin_id, destination_id, sl_api_key)

	if isinstance(route_info, str):
		print(route_info)
		return

	return create_response_route_info_message(route_info)


def manage_incoming_message_default_settings(prompt):
	f = open('./apikey.txt', 'r', encoding='utf-8')
	CHATGPT_API_KEY = f.readlines()[0]
	GPT_MODEL = "gpt-4o-mini"
	client = create_gpt3_client(CHATGPT_API_KEY)
	CURRENT_STATION_ID = "300109001"  # T-Centralen
	SL_API_KEY = "TRAFIKLAB-SLAPI-INTEGRATION-2024"
	return manage_incoming_message(prompt, client, GPT_MODEL, CURRENT_STATION_ID, SL_API_KEY)



def main():
	f = open('./apikey.txt', 'r', encoding='utf-8')
	CHATGPT_API_KEY = f.readlines()[0]
	GPT_MODEL = "gpt-4o-mini"
	client = create_gpt3_client(CHATGPT_API_KEY)
	CURRENT_STATION_ID = "300109001"  # T-Centralen
	SL_API_KEY = "TRAFIKLAB-SLAPI-INTEGRATION-2024"

	while True:
		print("")
		user_input = input("Where would you like to go? ")
		manage_incoming_message(user_input, client, GPT_MODEL, CURRENT_STATION_ID, SL_API_KEY)


if __name__ == "__main__":
    main()




