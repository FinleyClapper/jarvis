from pymicro_wakeword import MicroWakeWord, Model
import sounddevice as sd
SAMPLE_RATE = 16000
CHUNK_SIZE = 160
mww = MicroWakeWord.from_builtin(Model.HEY_JARVIS)
def audio_chunks():
    """Generator that yields 10ms audio chunks safely."""
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16', blocksize=CHUNK_SIZE) as stream:
        try:
            while True:
                chunk, _ = stream.read(CHUNK_SIZE)
                yield chunk.tobytes()
        except GeneratorExit:
            return
def detect_wake_word():
    """Detects wake word in a loop, returns True when detected."""
    for audio_bytes in audio_chunks():
        if len(audio_bytes) != CHUNK_SIZE * 2:
            continue
        if mww.process_streaming(audio_bytes):
            return True
