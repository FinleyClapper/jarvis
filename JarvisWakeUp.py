import numpy as np
def wake_word_detected(audio_chunk: np.ndarray, porcupine) -> bool:
    pcm = (audio_chunk * 32768).astype(np.int16).flatten()
    frame_length = porcupine.frame_length
    for i in range(0, len(pcm) - frame_length + 1, frame_length):
        frame = pcm[i:i+frame_length]
        if porcupine.process(frame) >= 0:
            return True
    return False