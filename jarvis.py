import speech_recognition as sr
import ollama
from TTS.api import TTS
import sounddevice as sd
from HeyJarvisv2 import JarvisListener
listener = JarvisListener(wake_word="jarvis", whisper_model="small")
listener.start()
tts = TTS("tts_models/en/ljspeech/glow-tts",gpu=True)
def speak(text):
    wav = tts.tts(text=text)
    sd.play(wav,samplerate=48000)
    sd.wait()

conversation_history = [{"role": "system", "content": "Keep responses below 50 words."}]

try:
    while True:
        command = listener.listen_for_command()
        if not command:
            continue
        print(f"You said: {command}")
        conversation_history.append({"role": "user", "content": command})

        # Send to LLM
        try:
            response = ollama.chat(model='llama3', messages=conversation_history)
            reply = response['message']['content']
            conversation_history.append({"role": "assistant", "content": reply})
            print(f"Jarvis: {reply}")
            speak(reply)
        except Exception as e:
            print("Error contacting Ollama:", e)
            speak("Sorry, I couldn't process that.")

except KeyboardInterrupt:
    listener.stop()