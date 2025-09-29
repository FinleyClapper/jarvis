#!/usr/bin/env python3
import os
import sys
import speech_recognition as sr
import pyttsx3
import ollama
from HeyJarvis import detect_wake_word
from TTS.api import TTS
import sounddevice as sd

stderr_fileno = sys.stderr
sys.stderr = open(os.devnull, 'w')


recognizer = sr.Recognizer()
engine = pyttsx3.init()


sys.stderr = stderr_fileno
tts = TTS("tts_models/en/jenny/jenny")
def speak(text):
    wav = tts.tts(text=text)
    sd.play(wav,samplerate=48000)
    sd.wait()


def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

conversation_history = [
    {"role": "system", "content": "Keep responses below 50 words."}
    #{"role": "system", "content": "You are Jarvis, a helpful and witty AI assistant."}
]

print("Jarvis is running... Say 'Hey Jarvis' to activate.")
def jarvis_activated():
        speak("Yes, how can I help you?")
        print("Wake word detected!")

        command = listen()
        print(f"You said: {command}")

        if command.strip() == "":
            speak("I didn't catch that. Please say it again.")
            return

        conversation_history.append({"role": "user", "content": command})

        try:
            response = ollama.chat(
                model='gpt-oss',
                messages=conversation_history
            )
            reply = response['message']['content']
            print(f"Jarvis: {reply}")
            speak(reply)

            # Append assistant reply to history
            conversation_history.append({"role": "assistant", "content": reply})
        except Exception as e:
            print("Error contacting Ollama:", e)
            speak("Sorry, I couldn't process that.")

while True:
    text = listen()
    if(detect_wake_word()):
        jarvis_activated()
    