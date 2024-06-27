# Near Realtime translater with whisper
# ====================================
# 1. use pyAudio to record voice streams
# ---------------------------------------
import pyaudio
import wave
import os
import pathlib

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
seconds = 3
sequence = 0

p = pyaudio.PyAudio()  # Create an interface to PortAudio

print("Recording")
print(f"recording under {os.getcwd()}")
cwd = os.getcwd()
if not f"{cwd}\\recording_room":
    os.makedirs(f"{cwd}\\recording_room")
while True:
    # record every 3 seconds save file then keep recording until stopped
    # {os.getcwd()}\recording_room\
    print(f'{cwd}\\recording_room\\sequence_{sequence}')
    filename = f"output_{sequence}.wav"
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    
    frames = []  # Initialize array to store frames
    
    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
    
    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    
    
    print('Finished small chuck recording')
    
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    sequence += 1

# Terminate the PortAudio interface - comment out if you want to keep recording
# print('Finished all recording')
#p.terminate(stream)