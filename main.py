import requests
import openai
from datetime import datetime

CHATGPT_API_KEY = ""
GPT_MODEL = "gpt-4o-mini"


"""
Context
Voice
SL API
Fancy frontend
Evals
"""


client = openai.OpenAI(api_key=CHATGPT_API_KEY)

def chat_with_gpt(prompt, model=GPT_MODEL):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": "You are an assistance for guiding people through the Stockholm Metro."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content  # Corrected response access



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
        print(f"Error making request: {e}")
        return None

def main():
	# Example station IDs
	api_key = "TRAFIKLAB-SLAPI-INTEGRATION-2024"  # Replace with your actual API key
	origin_station = "300109001"  # Example station ID
	dest_station = "300109117"    # Example station ID

	result = get_route(origin_station, dest_station, api_key)

	# print("result", result)

	if result and 'Trip' in result:
		# Get the first trip only
		trip = result['Trip'][0]
		leg_list = trip.get('LegList', {}).get('Leg', [])
		if leg_list:
			duration = trip.get('duration')
			print("\nTrip details:")
			for leg in leg_list:
				transport = leg.get('Product', {}).get('name', 'Walking')
				origin = leg['Origin']['name']
				destination = leg['Destination']['name']
				print(f"Take {transport} from {origin} to {destination}")
			print(f"Total duration: {duration} minutes")

if __name__ == "__main__":
    main()

# if __name__ == "__main__":
#     # user_input = input("You: ")
# 	origin = "1234"
# 	destination = "5678"
# 	route_info = get_route(origin, destination)



