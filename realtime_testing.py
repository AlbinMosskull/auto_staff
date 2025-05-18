import sounddevice as sd
import threading
import sounddevice as sd
import queue


from openai_realtime import OpenAIRealtimeClient


def run_program():
    SAMPLE_RATE = 24000  # OpenAI default output sample rate
    audio_q = queue.Queue()

    # Start a background output stream
    def audio_output_worker():
        with sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='float32',
            blocksize=1024
        ) as stream:
            while True:
                audio_chunk = audio_q.get()
                if audio_chunk is None:
                    break
                stream.write(audio_chunk)

    # Start audio playback thread
    threading.Thread(target=audio_output_worker, daemon=True).start()

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
