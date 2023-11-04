
# Near Realtime translater with whisper
# ====================================
# 2. use whisper to transcribe
# ----------------------------
import whisper
import os
from time import sleep
import openai
from typing import Any, Callable
import multiprocessing

LANGUAGE = 'french'
processed_files = []
model = whisper.load_model("base")
original_text_list = []
translated_text_list = []


def timeout_try_windows(audio_file: Any, model: Any, target_function:Callable):
    # create a queue to store result of the translated text
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=target_function, args=[audio_file, model, q])
    p.start()
    #timeout after 2 seconds
    p.join(2)
    try: 
        if p.is_alive():
            p.terminate()
            p.join()
            raise TimeoutError()
    except TimeoutError:
        print(f"sanctioned function {target_function.__name__} cause it sleeped too long: {p.exitcode}")
        print(p.exitcode)
        return {"text": ("nan","nan")}
    result = q.get_nowait()
    return {"text":result}

def translategpt(text):
    translated_text = openai.ChatCompletion("davinci", prompt="", text=text)
    return translated_text


def translate_speech(audio_data, model, queue):
    transcribed = model.transcribe(audio_data, language=LANGUAGE)
    translated = translategpt(result)
    queue.put(transcribed, translated)
    return (transcribed, translated)

while True:
    # get files
    files = [files for x,y, files in os.walk(".")][0]
    files = [ f for f in files if ".wav" in f]
    non_processed_file = sorted(list(set(files) - set(processed_files)), key= lambda x: int(x.split("_")[1].split(".")[0]))
    print(non_processed_file)
    if non_processed_file:
        for file in non_processed_file:
            print(f"processing {file}")
            # initiste this as a timed process that can not last more than 2 sec
            result = model.transcribe(file, language=LANGUAGE)
            result = timeout_try_windows(file, model, translate_speech)
            original_text_list.append(result["text"][0])
            print(f'original text: {result["text"][0]} \n')
            translate = result["text"][1]
            print(f'translated: {translate} \n')
            translated_text_list.append(translate)
            processed_files.append(file)
		
    else:
        print("no audio, sleeping ..")
        sleep(1)
