
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from backend import manage_incoming_message_default_settings as manage_incoming_message


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
