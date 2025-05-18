import requests
import json


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



def manage_route_planning_request(destination_name, origin_id, sl_api_key):
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


def construct_route_planning_realtime_tool():
    return {
        "type": "function",
        "name": "plan_route",
        "description": "Plans a route to a destination.",
        "parameters": {
          "type": "object",
          "properties": {
            "destination_name": {
              "type": "string",
              "description": "The name of the destination.",
            }
          },
          "required": ["destination_name"]
        }
    }


def provide_realtime_route_planning_response(destination_name, call_id, origin_id, sl_api_key):
    print("#### ROUTE PLANNING FUNCTION CALL ####")
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps({"route": manage_route_planning_request(destination_name, origin_id, sl_api_key)})
        }
    }

