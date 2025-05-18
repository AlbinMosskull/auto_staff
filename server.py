
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from time import sleep
import threading
import queue


from openai_realtime import OpenAIRealtimeClient
from audio_output import start_audio_output_worker

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

_pending_action = None
_pending_action_lock = threading.Lock()

def set_pending_action(action_data):
    """Safely sets the global _pending_action variable."""
    with _pending_action_lock:
        global _pending_action
        _pending_action = action_data
        print(f"Global _pending_action set by background logic: {_pending_action}")

def run_program():
    audio_q = queue.Queue()

    start_audio_output_worker(audio_q)

    def get_openai_api_key() -> str:
        f = open('./apikey.txt', 'r', encoding='utf-8')
        API_KEY = f.readlines()[0]
        return API_KEY

    realtime_client = OpenAIRealtimeClient(
        get_openai_api_key(), audio_q
    )
    realtime_client.set_pending_action_callback(set_pending_action)
    realtime_client.run()
    realtime_client.sleep_until_connected()

    print("WebSocket connection established.")
    print("Start talking to the assistant...")

    # Kill the thread after some time
    time_until_kill = 120
    realtime_client.keep_alive_for(time_until_kill)
    print("WebSocket connection closed.")

@app.route('/api/get_action', methods=['GET'])
def get_pending_action():
    """Frontend calls this periodically to check for actions from the backend."""

    print("polling for pending action...")

    action_to_return = None

    # Safely retrieve and clear the pending action
    with _pending_action_lock:
        global _pending_action
        action_to_return = _pending_action
        _pending_action = None


    if action_to_return:
        print("Retrieved new pending action:", action_to_return)
        return jsonify(action_to_return)
    else:
        return jsonify({"action": "none"})

@app.route('/api/start', methods=['POST'])
def start_program_endpoint():
    """Frontend calls this to start the program."""
    print("Received /api/start request.")

    # Clear any previous pending action when starting a new session
    set_pending_action(None)

    # Start the run_program logic in a separate thread
    thread = threading.Thread(target=run_program)
    # thread.daemon = True # Consider if you want the Flask server to exit if this thread is still running
    thread.start()
    print("Started run_program in a background thread.")

    # Respond immediately to the frontend that the program is starting
    return jsonify({"status": "program_starting", "message": "The background program is starting."})


if __name__ == '__main__':
    print("Starting Flask server for Stockholm Metro voice assistant...")
    print("Server running at http://localhost:5000")
    print("Ready to receive requests at:")
    print("- http://localhost:5000/api/record (for voice recording)")
    print("- http://localhost:5000/api/message (for text processing)")
    app.run(host='0.0.0.0', port=5000, debug=True)
