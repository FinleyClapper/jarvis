import pvporcupine
import sounddevice as sd
import whisper
import numpy as np
import queue
import threading
import time
import pvcobra
from typing import List
from JarvisWakeUp import wake_word_detected
from DetectSpeech import Cobra
class JarvisListener:
    def __init__(self, wake_word: List[str] = ['jarvis', 'Jarvis', 'Hey Jarvis'] , whisper_model="small", samplerate=16000, blocksize=512):
        self.porcupine = pvporcupine.create(keywords=[wake_word],access_key="SAmquBGin2ukRyiEJfSctw4e5RlyTnaWNwwtEwShbYVY5XkVqmgHVw==")
        self.cobra = Cobra(score_buffer_size=10,score_threshold=.15)
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.whisper_model = whisper.load_model(whisper_model)
        self.audio_queue = queue.Queue()
        self._running = False
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            blocksize=self.blocksize,
            callback=self._audio_callback
        )
    def _audio_callback(self, indata, frames, time_info, status):
        self.audio_queue.put(indata.copy())

    def start(self):
        self._running = True
        self.stream.start()
        print("StreamingJarvisListener started.")

    def stop(self):
        self._running = False
        self.stream.stop()
        self.stream.close()
        self.porcupine.delete()
        print("StreamingJarvisListener stopped.")

    def _capture_speech_streaming(self, max_duration=5.0, silence_threshold=0.01, chunk_duration=0.5):
        start_time = time.time()
        audio_buffer = np.zeros(0, dtype=np.float32)

        while time.time() - start_time < max_duration:
            if not self.audio_queue.empty():
                chunk = self.audio_queue.get().flatten().astype(np.float32)
                # Normalize chunk
                if np.max(np.abs(chunk)) > 0:
                    chunk = chunk / np.max(np.abs(chunk))
                    audio_buffer = np.concatenate([audio_buffer, chunk])

                if not self.cobra.is_speaking(chunk):
                    print('here')
                    break
            else:
                time.sleep(0.01)

        if len(audio_buffer) == 0:
            return ""
        # Final transcription
        result = self.whisper_model.transcribe(audio_buffer, fp16=False)
        return result['text'].lower()

    def listen_for_command(self, max_duration: int = 5.0):
        print("Listening for wake word...")
        while self._running:
            if not self.audio_queue.empty():
                chunk = self.audio_queue.get()
                if wake_word_detected(audio_chunk=chunk,porcupine=self.porcupine):
                    print("Wake word detected! Listening to command...")
                    return self._capture_speech_streaming(max_duration=max_duration)
            else:
                time.sleep(0.01)
        return ""
