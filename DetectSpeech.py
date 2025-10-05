import numpy as np
from collections import deque
import pvcobra
class Cobra:
    def __init__(self, score_buffer_size: int, score_threshold: str):
        self.cobra = pvcobra.create(access_key="SAmquBGin2ukRyiEJfSctw4e5RlyTnaWNwwtEwShbYVY5XkVqmgHVw==")
        self.score_buffer_size = score_buffer_size
        self.score_threshold = score_threshold
        self.score_buffer = deque(maxlen=self.score_buffer_size)
        self.speech_began = False
    def is_speaking(self, audio_buffer: np.ndarray) -> bool:
            print(self.__get_buffer_average_score())
            if len(audio_buffer) != self.cobra.frame_length:
                return False
            pcm = (audio_buffer * 32767).astype(np.int16)
            self.score_buffer.append(self.cobra.process(pcm))
            if len(self.score_buffer) < self.score_buffer_size:
                return True
            if(self.__get_buffer_average_score() > self.score_threshold):
                self.speech_began = True
                return True
            elif(self.speech_began):
                self.__clear_buffer()
                return False
    def __get_buffer_average_score(self) -> float:
        return (sum(self.score_buffer) / self.score_buffer_size)
    def __clear_buffer(self):
        self.score_buffer = deque(maxlen=self.score_buffer_size)
        self.speech_began = False