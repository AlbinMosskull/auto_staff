import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
import simpleaudio as sa
from openai import OpenAI
import os
import time
import random
import numpy as np

def speech_to_text(record=True, play_recording=False) -> str:
    """
    Interface to convert a voice request to text

    Parameters:
    record (boolean): True -> record from microphone
                      False -> use random pre-recorded sample
    play_recording (boolean) : True -> play the recording
                               False -> do not play the recording

    Returns:
    str: Transcription of the voice request
    """
    # Create OpenAI client
    client = OpenAI(api_key=_get_api_key_dev())

    # Get voice recording
    voice_recording_path = ""
    if record:
        voice_recording_path = _record_voice_request_dyn()
    else:
        voice_recording_path = _pick_random_prerecorded_request()

    # Optionally, replay the recording. Mainly for debugging pruposes
    if play_recording:
        _play_recording(voice_recording_path)

    # Transcribe the recording
    voice_file = open(voice_recording_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=voice_file
    )

    return transcription.text


def text_to_speech(text: str, play_result: bool=True) -> str:
    """
    Interface to convert text to speech

    Parameters:
    text: The text that should be converted

    Returns:
    str: file path to a .mp3 file of the speech
    """
    client = OpenAI(api_key=_get_api_key_dev())
    mp3_path = os.path.join(os.path.dirname(__file__), "voice_out", "tmp", "speech.mp3")
    
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        response_format="mp3"
    ) as response:
        response.stream_to_file(mp3_path)
    
    if play_result:
        _play_recording(mp3_path)

    return mp3_path


def _get_api_key_dev() -> str:
    """
    Get a ChatGPT (dev) api key from local file

    Returns:
    str: api key
    """
    f = open('./apikey.txt', 'r', encoding='utf-8')
    api_key = f.readlines()[0]

    return api_key


def _pick_random_prerecorded_request() -> str:
    """
    Pick a random voice recording with directions.

    Returns:
    str: file path to recording
    """
    files = [f for f in os.listdir("voice_in/examples") if os.path.isfile(os.path.join("voice_in/examples", f))]
    if not files:
        raise FileNotFoundError("No files found in the folder: voice_in/examples/")
    
    random_file = random.choice(files)
    random_file_path = f"voice_in/examples/{random_file}"

    return random_file_path


def _record_voice_request() -> str:
    """
    Record a voice request with directions of where to go

    Returns:
    str: file path to .mp3 file of voice recording
    """
    folder = "voice_in/tmp"
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder '{folder}' does not exist. Please create it first.")

    # Recording settings
    duration = 8  # seconds
    sample_rate = 44100  # Hz

    print("Recording ...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype=np.int16)
    sd.wait()
    print("Recording finished.")

    # Save as WAV temporarily
    wav_path = os.path.join(folder, "temp_recording.wav")
    write(wav_path, sample_rate, audio_data)

    # Convert to MP3
    mp3_path = os.path.join(folder, "recording.mp3")
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3")

    # Remove temporary WAV file
    os.remove(wav_path)

    print(f"Saved as {mp3_path}")

    return mp3_path

def _record_voice_request_dyn() -> str:
    """
    Record a voice request dynamically and stop when silence is detected.

    Returns:
    str: file path to .mp3 file of voice recording
    """
    folder = "voice_in/tmp"
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder '{folder}' does not exist. Please create it first.")

    # Recording settings
    sample_rate = 16000  # Hz
    max_duration = 20  # seconds
    silence_threshold = 100  # Amplitude threshold for silence detection
    silence_duration = 2.0  # Stop recording after x second of silence
    min_speech_time = 5.0 # Ensure at least 2 s of speech before stopping

    print("Recording ...")
    start_time = time.time()
    silence_start = None
    audio_data = []
    stop_recording = False

    def callback(indata, frames, time_info, status):
        nonlocal silence_start, stop_recording

        if status:
            print(status)

        # Append audio chunk to data list
        audio_data.append(indata.copy())

        # Calculate amplitude
        amplitude = np.abs(indata).mean()

        # Ensure minimum speech time before stopping
        elapsed_time = time.time() - start_time
        if elapsed_time < min_speech_time:
            return

        # Silence detection logic
        if amplitude < silence_threshold:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start > silence_duration:
                stop_recording = True  # Set flag to stop recording
        else:
            silence_start = None  # Reset silence timer if speaking resumes

        # Stop after max duration
        if elapsed_time >= max_duration:
            stop_recording = True

    # Start recording
    with sd.InputStream(samplerate=sample_rate, channels=2, dtype=np.int16, callback=callback):
        while not stop_recording:
            sd.sleep(100)  # Sleep for a short period to allow audio processing

    print("Recording finished.")

    # Convert list of chunks into a NumPy array
    audio_data = np.concatenate(audio_data, axis=0)

    # Save as WAV temporarily
    wav_path = os.path.join(folder, "temp_recording.wav")
    write(wav_path, sample_rate, audio_data)

    # Convert to MP3
    mp3_path = os.path.join(folder, "recording.mp3")
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3")

    # Remove temporary WAV file
    os.remove(wav_path)

    print(f"Saved as {mp3_path}")

    return mp3_path


def _play_recording(mp3_path: str):
    """
    Play a voice recording

    Parameters:
    mp3_path: file path to a .mp3 file to play
    """
    print("Playing the recording ...")
    audio = AudioSegment.from_mp3(mp3_path)
    play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
    play_obj.wait_done()
    print("Playback finished.")


if __name__ == "__main__":
    print(speech_to_text(record=True, play_recording=True))
    # text_to_speech("Take the blue line 10 for 5 stops. Estimated travel time: 7 min.")
