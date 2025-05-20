from faster_whisper import WhisperModel, BatchedInferencePipeline

_WHISPER = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=4, num_workers=6)
_BATCHED_MODEL = BatchedInferencePipeline(_WHISPER)

class Transcriber:
    def transcribe(audio_path):
        segments, _ = _BATCHED_MODEL.transcribe(
            audio_path,
            language="ru",
            beam_size=3,
            best_of=2,
            word_timestamps=True,
            vad_filter=True
        )

        return [
            {"start": round(word.start, 2), "end": round(word.end, 2), "word": word.word}
            for segment in segments
            for word in segment.words
        ]