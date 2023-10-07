
# Near Realtime translater with whisper
# ====================================
# 2. use whisper to transcribe
# ----------------------------
import whisper
import os
from time import sleep

LANGUAGE = 'french'
processed_files = []
model = whisper.load_model("base")
original_text_list = []
translated_text_list = []
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
            # translate = openai.translate(result)
            original_text_list.append(result["text"])
            print(f'original text: {result["text"]} \n')
            # print(f'translated: {translate} \n')
            # translated_text_list.append(translate)
            processed_files.append(file)
		
    else:
        print("no audio, sleeping ..")
        sleep(1)
