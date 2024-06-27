
# Near Realtime translater with whisper
# ====================================
# 2. use whisper to transcribe
# ----------------------------
import whisper
import os
from typing import Any, Callable
import multiprocessing
from chat_translator import translate

LANGUAGE = 'french'
TO_LANGUAGE = "English"
processed_files = []
model = whisper.load_model("medium")
original_text_list = []
translated_text_list = []


def timeout_try_windows(audio_file: Any, model: Any, target_function:Callable):
    # create a queue to store result of the translated text
    q = multiprocessing.Queue()
    print("-"*100)
    p = multiprocessing.Process(target=target_function, args=[audio_file, model, q])
    p.start()
    p.join(3)
    try: 
        if p.is_alive():
            p.terminate()
            p.join()
    except TimeoutError:
        print(f"sanctioned function {target_function.__name__} cause it waited too long: {p.exitcode}")
        return {"text": ("nan","nan")}
    result = q.get_nowait()
    return {"text":result}


def translate_speech(audio_data, model, queue):
    transcribed = model.transcribe(audio_data, language=LANGUAGE)
    print(f"transcribed as {transcribed}")
    translated = translate(transcribed["text"], LANGUAGE, TO_LANGUAGE)
    print(f"translated as {translated}")
    queue.put((transcribed["text"], translated))
    return (transcribed, translated)


if __name__ == "__main__":
    files = [files for x,y, files in os.walk("./audio/")][0]
    files = [ f for f in files if ".wav" in f]
    non_processed_file = sorted(list(set(files) - set(processed_files)), key= lambda x: int(x.split("_")[1].split(".")[0]))
    for _file in non_processed_file:
        sample_file = "./audio/"+_file
        print(f"working on {sample_file}")
        result = timeout_try_windows(sample_file, model, translate_speech)
        print("="*50)
        print(f"result is: {result}")
        print("="*50)
