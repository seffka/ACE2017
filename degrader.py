# produces degraded versions of the dataset.
# 1) converted to MP3.
# 3) downsampling.
from subprocess import call
import os

original_audio_path = "/Users/seffka/Desktop/MIR/Beatles/audio"
base_path = "/Users/seffka/Desktop/MIR/Beatles"


# convert content of original_audio_path to MP3
# and put it into b<bit rate> directory.
def toMP3():
    mp3configs = ['b32', 'b64', 'b128', 'b320', 'V2', 'V4', 'V6']
    for p in mp3configs:
        os.mkdir(os.path.join(base_path, p))
    for file in [f for f in os.listdir(original_audio_path) if os.path.isfile(os.path.join(original_audio_path, f))] :
        name, ext = os.path.splitext(file)
        print ext
        if (ext == '.wav' or ext == '.flac'):
            for p in mp3configs:
                call(['lame', '-' + p, os.path.join(original_audio_path, file), os.path.join(base_path, p, name + ".mp3")])

# downsample content of original_audio_path
# and put it into down<sample rate> directory.
def downSample():
    rates = ['22050', '11025', '5512']
    for r in rates:
        os.mkdir(os.path.join(base_path, 'down' + r))
    for file in [f for f in os.listdir(original_audio_path) if os.path.isfile(os.path.join(original_audio_path, f))] :
        name, ext = os.path.splitext(file)
        print ext
        if (ext == '.wav' or ext == '.flac'):
            for r in rates:
                call(['ffmpeg', '-i', os.path.join(original_audio_path, file), '-ar', r, os.path.join(base_path, 'down' + r, file)])

toMP3()
downSample()


