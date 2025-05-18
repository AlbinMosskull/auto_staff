import threading
import queue


from openai_realtime import OpenAIRealtimeClient
from audio_output import start_audio_output_worker


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
    realtime_client.run()
    realtime_client.sleep_until_connected()

    print("WebSocket connection established.")
    print("Start talking to the assistant...")

    # Kill the thread after some time
    time_until_kill = 60
    realtime_client.keep_alive_for(time_until_kill)
    print("WebSocket connection closed.")


if __name__ == "__main__":
    run_program()
