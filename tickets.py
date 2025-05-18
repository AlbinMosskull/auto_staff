import json


_TICKET_TYPES = {
    "single": {"normal": 43, "retiree": 26, "student": 26, "youth": 26},
    "24h": {"normal": 180, "retiree": 110, "student": 110, "youth": 110},
    "72h": {"normal": 360, "retiree": 220, "student": 220, "youth": 220},
    "7d": {"normal": 470, "retiree": 290, "student": 290, "youth": 290},
    "30d": {"normal": 1060, "retiree": 650, "student": 650, "youth": 650},
    "90d": {"normal": 3070, "retiree": 1880, "student": 1880, "youth": 1880},
    "annual": {"normal": 11130, "retiree": 6830, "student": 6830, "youth": 6830}
}

def get_ticket_types():
	return list(_TICKET_TYPES.keys())

def get_traveler_types():
	return list(_TICKET_TYPES["single"].keys())

def get_price(ticket_type, traveler_type):
    return _TICKET_TYPES.get(ticket_type, {}).get(traveler_type, None)


def format_ticket_info(ticket_type, traveler_type):
	# Hack below. Seems to be needed for openai api.
	return str(f"Ticket type: {ticket_type}, Traveler type: {traveler_type}, Price: {get_price(ticket_type, traveler_type)} SEK")


def parse_ticket_info(ticket_type, traveler_type):
	ticket_info = format_ticket_info(ticket_type, traveler_type)
	print(ticket_info)
	return ticket_info

def construct_ticket_purchase_tool():
	return {
        "type": "function",
        "name": "purchase_ticket",
        "description": "Purchase a ticket.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_type": {
                    "type": "string",
                    "description": "The type of ticket to purchase.",
                    "enum": get_ticket_types()
                },
                "traveler_type": {
                    "type": "string",
                    "description": "The type of traveler.",
                    "enum": get_traveler_types()
                }
            },
            "required": ["ticket_type", "traveler_type"]
        }
    }


def provide_realtime_ticket_purchase_response(ticket_type, traveler_type, call_id):
    print("#### TICKET FUNCTION CALL ####")
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps({"Ticket": parse_ticket_info(ticket_type, traveler_type)})
        }
    }

