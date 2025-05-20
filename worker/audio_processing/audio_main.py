import os
from audio_processing.preprocessing import Preprocessing
from audio_processing.diarization import Diarization
from audio_processing.transcribe import Transcriber
from audio_processing.align_result import AlignTextWithDiarization
from audio_processing.audio_identify import AudioIdentify
from concurrent.futures import ThreadPoolExecutor

class HandleAudio:
    def start_handle(audio_path):
        processed_path, is_tmp = Preprocessing.preprocess_audio(audio_path)

        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_transcribe = executor.submit(Transcriber.transcribe, processed_path)
                future_diarization = executor.submit(Diarization.diarization, processed_path)
                
                transcribe_result = future_transcribe.result()
                diarization_result = future_diarization.result()

                future_identify = executor.submit(AudioIdentify.send_request, processed_path, diarization_result)
                identify_result = future_identify.result()

                align_result = AlignTextWithDiarization.align_results(transcribe_result, diarization_result, identify_result)

                return align_result
        finally:
            if is_tmp and os.path.exists(processed_path):
                os.unlink(processed_path)