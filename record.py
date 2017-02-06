def check_valid_user_int(user_input):
	try:
		int(user_input)
		return True
	except ValueError:
		return False

import os
import subprocess
import pyaudio
import wave
from ffmpy import FFmpeg
dir_name = os.getcwd()
print dir_name

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = dir_name + '/recordings/output.wav'
FLAC_OUTPUT_FILENAME = dir_name + '/recordings/output.flac'
RAW_OUTPUT_FILENAME = dir_name + '/recordings/output.raw'

p = pyaudio.PyAudio()

# STEP 0: remove old files
subprocess.call(["rm", WAVE_OUTPUT_FILENAME])
subprocess.call(["rm", FLAC_OUTPUT_FILENAME])
subprocess.call(["rm", RAW_OUTPUT_FILENAME])

# STEP 1: get all recording devices
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
valid_ids = set()
for i in range(0, numdevices):
	if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
		valid_ids.add(i)
		print 'Recording device ID', i, ' - ', p.get_device_info_by_host_api_device_index(0, i).get('name')

# STEP 2: ask user to select recording device
prompt = 'Select the ID of the device you would like to record from: '
user_input = raw_input(prompt)
while not check_valid_user_int(user_input) or int(user_input) not in valid_ids:
	print 'Please enter a valid ID from the device list: ' + str(list(valid_ids))
	user_input = raw_input(prompt)
selected_id = int(user_input)

# STEP 3: set up input stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=selected_id)

frames = []
user_input = None

# STEP 4: record from selected device
print 'STARTING RECORDING NOW (press [CTRL-C] when you would like to finish recording)'
try:
	while True:
		data = stream.read(CHUNK)
		frames.append(data)
except KeyboardInterrupt:
	pass
print 'ENDING RECORDING NOW'

stream.stop_stream()
stream.close()
p.terminate()

# STEP 5: save audio frames as .wav
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# STEP 6: convert .wav to .flac/raw for ASR
# ff = FFmpeg(
# 	inputs = {WAVE_OUTPUT_FILENAME: None},
# 	outputs = {FLAC_OUTPUT_FILENAME: None})
# ff.run()

ff = FFmpeg(
	inputs = {WAVE_OUTPUT_FILENAME: None},
	outputs = {RAW_OUTPUT_FILENAME: '-f s16le -acodec pcm_s16le -ac 1'})
ff.run()
