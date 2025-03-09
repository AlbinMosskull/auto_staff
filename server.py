
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def manage_incoming_message(user_input):
    """
    This is where your custom logic would go.
    You could integrate with OpenAI, SL APIs, or any other services here.
    
    For this example, we're just returning a dummy response with the user input echoed back.
    """
    
    # Example response format
    response = f"You asked about: '{user_input}'. Here's information about Stockholm metro stations..."
    
    # You could add more sophisticated processing here:
    if "t-centralen" in user_input.lower():
        response = "T-Centralen is the central station in Stockholm's metro system, connecting all lines."
    elif "red line" in user_input.lower():
        response = "The Red Line (Röda linjen) consists of lines 13 and 14, running from Norsborg/Fruängen to Ropsten/Mörby Centrum."
    elif "blue line" in user_input.lower():
        response = "The Blue Line (Blå linjen) consists of line 10 and 11, running from Kungsträdgården to Hjulsta/Akalla."
    
    return response

@app.route('/api/message', methods=['POST'])
def process_message():
    """
    Endpoint that receives messages from the frontend
    """
    data = request.json
    user_input = data.get('user_input', '')
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    # Call your custom function to process the message
    response = manage_incoming_message(user_input)
    
    # Return the response to the frontend
    return jsonify({"response": response})

if __name__ == '__main__':
    print("Starting Flask server for Stockholm Metro assistant...")
    print("Server running at http://localhost:5000")
    print("Ready to receive requests at http://localhost:5000/api/message")
    app.run(host='0.0.0.0', port=5000, debug=True)
