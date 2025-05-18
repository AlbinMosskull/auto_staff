import threading
import sounddevice as sd

def start_audio_output_worker(audio_q):
    SAMPLE_RATE = 24000  # OpenAI default output sample rate

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