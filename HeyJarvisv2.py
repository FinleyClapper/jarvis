import pvporcupine
import sounddevice as sd
import whisper
import numpy as np
import queue
import threading
import time

class JarvisListener:
    def __init__(self, wake_word="jarvis", whisper_model="small", samplerate=16000, blocksize=512):
        """
        wake_word: keyword to trigger listening
        whisper_model: Whisper model for transcription
        samplerate: microphone sample rate
        blocksize: number of samples per audio callback
        """
        self.porcupine = pvporcupine.create(keywords=[wake_word],access_key="SAmquBGin2ukRyiEJfSctw4e5RlyTnaWNwwtEwShbYVY5XkVqmgHVw==")
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
        """Put audio chunks into queue"""
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

    def _wake_word_detected(self, audio_chunk):
        pcm = (audio_chunk * 32768).astype(np.int16).flatten()
        frame_length = self.porcupine.frame_length
        for i in range(0, len(pcm) - frame_length + 1, frame_length):
            frame = pcm[i:i+frame_length]
            if self.porcupine.process(frame) >= 0:
                return True
        return False

    def _capture_speech_streaming(self, max_duration=5.0, silence_threshold=0.01, chunk_duration=0.5):
        """
        Capture audio in small chunks and stream to Whisper.
        Stop after max_duration or silence.
        Returns final transcription.
        """
        start_time = time.time()
        audio_buffer = np.zeros(0, dtype=np.float32)
        last_speech_time = time.time()

        while time.time() - start_time < max_duration:
            if not self.audio_queue.empty():
                chunk = self.audio_queue.get().flatten().astype(np.float32)
                # Normalize chunk
                if np.max(np.abs(chunk)) > 0:
                    chunk = chunk / np.max(np.abs(chunk))
                audio_buffer = np.concatenate([audio_buffer, chunk])

                # Detect speech activity
                if np.max(np.abs(chunk)) > silence_threshold:
                    last_speech_time = time.time()

                # Stop if silence after minimum speech duration
                if time.time() - last_speech_time > chunk_duration:
                    break
            else:
                time.sleep(0.01)

        if len(audio_buffer) == 0:
            return ""

        # Final transcription
        result = self.whisper_model.transcribe(audio_buffer, fp16=False)
        return result['text'].lower()

    def listen_for_command(self, max_duration=5.0):
        """
        Wait for wake word, then capture and transcribe speech in streaming mode.
        Returns final text command.
        """
        print("Listening for wake word...")
        while self._running:
            if not self.audio_queue.empty():
                chunk = self.audio_queue.get()
                if self._wake_word_detected(chunk):
                    print("Wake word detected! Listening to command...")
                    return self._capture_speech_streaming(max_duration=max_duration)
            else:
                time.sleep(0.01)
        return ""
