import os
from pyannote.audio import Pipeline

_DIARIZATION = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token=os.getenv("HF_TOKEN"))

class Diarization:
    def diarization(audio_path):
        diar = _DIARIZATION(audio_path)

        return [
            {"speaker": speaker, "start": round(turn.start, 2), "end": round(turn.end, 2)}
            for turn, _, speaker in diar.itertracks(yield_label=True)
        ]