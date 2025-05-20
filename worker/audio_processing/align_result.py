class AlignTextWithDiarization:
    def assign_speakers(words, turns, min_ratio=0.5):
        turns = sorted(turns, key=lambda t: t["start"])
        out = []
        last_speaker = "UNKNOWN"

        for word in words:
            start_word, end_word = word["start"], word["end"]
            best_lbl, best_ov = None, 0.0

            for turn in turns:
                if turn["end"] < start_word:
                    continue
                if turn["start"] > end_word:
                    break          
                ov = min(turn["end"], end_word) - max(turn["start"], start_word)
                if ov > best_ov:
                    best_ov, best_lbl = ov, turn["speaker"]

            if best_lbl and best_ov / (end_word - start_word) >= min_ratio:
                word["speaker"] = best_lbl
                last_speaker = best_lbl
            else:
                word["speaker"] = last_speaker

            out.append(word)

        return out

    def align_speakers(result_text, speakers):
        for speaker in speakers:
            result_text = result_text.replace(speaker['speaker'], speaker['speaker_name'])

        return result_text

    def align_results(transcribe_data, diarization_data, speakers, max_pause=1.0):
        tagged_words = AlignTextWithDiarization.assign_speakers(transcribe_data, diarization_data)

        utter, cur = [], None
        for word in tagged_words:
            if (cur is None or
                word["speaker"] != cur["speaker"] or
                word["start"] - cur["end"] > max_pause):
                if cur: utter.append(cur)
                cur = {"speaker": word["speaker"],
                    "start":   word["start"],
                    "end":     word["end"],
                    "text":    word["word"]}
            else:
                cur["end"]  = word["end"]
                cur["text"] += " " + word["word"]
        if cur: utter.append(cur)

        aligned_text = "\n".join(f"[{u['speaker']}] {u['text']}" for u in utter)

        result_text = AlignTextWithDiarization.align_speakers(aligned_text, speakers)

        return result_text
    
    
