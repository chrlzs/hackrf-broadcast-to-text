import sys
import os
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Load Vosk model
model_path = "model"  # Path to the Vosk model directory
if not os.path.exists(model_path):
    print(f"Error: Vosk model not found at {model_path}. Please download a model from https://alphacephei.com/vosk/models.")
    sys.exit(1)

model = Model(model_path)
samplerate = 16000  # Sample rate for audio input
device = None  # Use the default audio input device (set to a specific device ID if needed)

# Create a queue for audio data
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Callback function to capture audio data."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def main():
    # Initialize recognizer
    recognizer = KaldiRecognizer(model, samplerate)

    # Start audio stream
    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=8192,
        device=device,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        print("Listening... Press Ctrl+C to stop.")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                print(result)  # Print the final transcription result
            else:
                partial_result = recognizer.PartialResult()
                print(partial_result)  # Print partial results (interim transcriptions)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTranscription stopped.")