import librosa
import tempfile
import os
import soundfile as sf

class Preprocessing:
    def preprocess_audio(audio_path):
        y, sr = librosa.load(audio_path, sr=None, mono=True)

        if sr == 16000:
            return audio_path, False
        
        y_16k = librosa.resample(y, orig_sr=sr, target_sr=16000)

        dir_name = os.path.dirname(audio_path)

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", dir=dir_name, delete=False)

        sf.write(tmp.name, y_16k, 16000)
        tmp.close()

        return tmp.name, True