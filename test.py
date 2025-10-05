import pvcobra
                if self.cobra_stream(chunk):
                    last_speech_time = time.time()

                # Stop if silence after minimum speech duration
                if time.time() - last_speech_time > chunk_duration:
                    break
    def cobra_stream(self, audio_buffer: np.ndarray) -> bool:
        # Cobra expects 16-bit PCM, not float32
        if len(audio_buffer) != self.cobra.frame_length:
            return False

        # Convert to int16 PCM
        pcm = (audio_buffer * 32767).astype(np.int16)

        # Process expects int16 array, not bytes
        score = self.cobra.process(pcm)
        print("Cobra score:", score)
        return score > 0.5
    