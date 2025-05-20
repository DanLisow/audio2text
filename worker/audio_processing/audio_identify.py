import requests
from pathlib import Path

identify_url = "http://95.163.223.152:8000/identify/"

class AudioIdentify:
    def send_request(audio_path, diar):
        filename = Path(audio_path).name

        formatted_input = "\n".join(
            f"{item['speaker']}://{item['start']:.2f}-{item['end']:.2f}"
            for item in diar
        )

        with open(audio_path, "rb") as f:
            files = {
                "audio_file": (filename, f, "audio/wav"),
                "request": (None, formatted_input)
            }
            resp = requests.post(identify_url, files=files)

            try:
                response_data = resp.json()
                
                if isinstance(response_data, list):

                    processed_data = []

                    for item in response_data:
                        if isinstance(item, dict):

                            segment = item.get('segment', '')
                            speaker = segment.split('://')[0] if '://' in segment else ''
                            
                            speaker_name = item.get('speaker_name', '')
                            status = item.get('status', '')
                            
                            if speaker and speaker_name and "Ошибка обработки" not in status:
                                processed_data.append({
                                    'speaker': speaker,
                                    'speaker_name': speaker_name
                                })
                    
                    unique_data = []
                    seen = set()
                    for item in processed_data:
                        key = (item['speaker'], item['speaker_name'])
                        if key not in seen:
                            seen.add(key)
                            unique_data.append(item)
                    
                    return unique_data
                
                return []
            
            except ValueError as e:
                print(f"Ошибка декодирования JSON: {e}")
                return []
            except Exception as e:
                print(f"Ошибка обработки ответа: {e}")
                return []