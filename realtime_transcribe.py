import socket
import queue
from vosk import Model, KaldiRecognizer

# Load Vosk model
model = Model("model")  # Path to the Vosk model directory
samplerate = 16000  # Sample rate for audio input

# Create a queue for audio data
q = queue.Queue()

def receive_audio():
    """Receive audio data from GNU Radio via TCP."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 12345))  # Bind to the same IP and port as GNU Radio
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                q.put(data)

def main():
    # Initialize recognizer
    recognizer = KaldiRecognizer(model, samplerate)

    # Start receiving audio data
    receive_audio()

    # Process audio data
    while True:
        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            print(result)  # Print the final transcription result
        else:
            partial_result = recognizer.PartialResult()
            print(partial_result)  # Print partial results (interim transcriptions)

if __name__ == "__main__":
    main()