import time
import pvporcupine
import sounddevice as sd
import numpy as np
import pyttsx3
import ollama
import queue
import speech_recognition as sr
import threading

# -----------------------------
# Text-to-speech setup
# -----------------------------
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# -----------------------------
# Conversation history for Ollama
# -----------------------------
conversation_history = [
    {"role": "system", "content": "You are Jarvis, a helpful and witty AI assistant."}
]

# -----------------------------
# Porcupine hotword setup
# -----------------------------
porcupine = pvporcupine.create(
    access_key='SAmquBGin2ukRyiEJfSctw4e5RlyTnaWNwwtEwShbYVY5XkVqmgHVw==',
    keywords=["jarvis"]
)
q = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    pcm = np.array(indata[:, 0] * 32768, dtype=np.int16)
    q.put(pcm)

# -----------------------------
# Frame buffer for Porcupine
# -----------------------------
frame_length = porcupine.frame_length
buffer = np.zeros(frame_length, dtype=np.int16)
buf_index = 0

# -----------------------------
# Real-time speech-to-text and command handling
# -----------------------------
def listen_and_process():
    recognizer = sr.Recognizer()
    samplerate = 16000
    channels = 1
    chunk_duration = 0.5  # seconds
    chunk_size = int(samplerate * chunk_duration)

    print("Debug: Listening for command (real-time)...")
    accumulated_text = ""

    with sd.InputStream(samplerate=samplerate, channels=channels, dtype='int16') as stream:
        silent_chunks = 0
        while True:
            data, overflow = stream.read(chunk_size)
            audio_chunk = np.squeeze(data)
            audio_data = sr.AudioData(audio_chunk.tobytes(), samplerate, 2)

            try:
                text = recognizer.recognize_google(audio_data)
                if text.strip():
                    print("Heard:", text)
                    accumulated_text += " " + text
                    silent_chunks = 0
            except sr.UnknownValueError:
                silent_chunks += 1
            except sr.RequestError:
                print("Speech service unavailable")

            # Stop listening if silence detected for ~1s (2 chunks)
            if silent_chunks >= 2:
                break

    command = accumulated_text.strip()
    if command == "":
        speak("Sorry, I did not catch that.")
        return

    print(f"Full command: {command}")
    conversation_history.append({"role": "user", "content": command})
    try:
        response = ollama.chat(
            model='llama3',
            messages=conversation_history
        )
        reply = response['message']['content']
        print(f"Jarvis: {reply}")
        speak(reply)
        conversation_history.append({"role": "assistant", "content": reply})
    except Exception as e:
        print("Error contacting Ollama:", e)
        speak("Sorry, I couldn't process that.")

# -----------------------------
# Main loop: continuous wake-word detection
# -----------------------------
print("Jarvis is running... Say 'Jarvis' to activate.")

with sd.InputStream(channels=1, callback=audio_callback, samplerate=porcupine.sample_rate):
    try:
        while True:
            if not q.empty():
                pcm_chunk = q.get()
                for sample in pcm_chunk:
                    buffer[buf_index] = sample
                    buf_index += 1

                    if buf_index == frame_length:
                        buf_index = 0
                        result = porcupine.process(buffer)
                        if result >= 0:
                            print("Wake word detected!")
                            speak("Yes, how can I help you?")
                            threading.Thread(target=listen_and_process).start()

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Exiting Jarvis...")
