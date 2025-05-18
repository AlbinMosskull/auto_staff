import pandas as pd

def get_available_destinations():
    response = {"type" : "available_destinations"}
    
    df = pd.read_csv('sites_list.csv', header=None)
    destinations = df[0].dropna().unique().tolist()
    response["destinations"] = destinations

    return response

def construct_available_destinations_tool():
    return {
        "type": "function",
        "name": "get_available_destinations",
        "description": "Get a list of all available destinations."
    }