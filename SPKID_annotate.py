#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 10:28:09 2021

@author: jack

Input: 2-channel audio
    wav format: -r 16k -b 16 -e signed 
    name: file_{session}_doc.wav, file_{session}_kid.wav

這個腳本用來自動化生出醫生與小孩的話語始末標記，方法如下：
    1. 用webrtc先對doc 和 KID 都做VAD
    2. 比對energy（用librosa的rms算）的方式來決定這個是不是屬於自己的frame
        2. 在自己（doc/kid）的secment裡面如果自己的energy小於對方的就不納入，不然就將這個segment標記成自己的role
    

"""
import sys
# sys.path.append("/media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata")
import librosa
import numpy as np
import subprocess
# from CryingCLF_VAD import Predictor, Pred_gbm, essentia_Feat
from functools import partial
import pdb 
from collections import defaultdict
import pandas as pd
import joblib
from scipy.signal import correlate
import datetime
from joblib import Parallel, delayed
import glob
from itertools import permutations
import os
import argparse
import webrtcvad
import wave
import contextlib
import collections
from pyannote.core import Segment, Annotation


def Annotate_CmpEnergy(segments,data_self,data_other,role='doc'):
    annotation = Annotation()
    for i in range(len(segments)):
        start_n = int(segments[i][0] * rate)
        end_n = int(segments[i][1] * rate)
        
        energy_self=np.sum(librosa.feature.rms(data_self[start_n:end_n]))
        energy_other=np.sum(librosa.feature.rms(data_other[start_n:end_n]))
        
        if energy_self > energy_other:
            annotation[Segment(segments[i][0],segments[i][1])]=role
        
    return annotation
def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.
    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.
    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.
    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.
    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.
    Arguments:
    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).
    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        sys.stdout.write('1' if is_speech else '0')
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])


def Get_VADBool(frames):
    VAD_bool=[]
    VAD_timestamp=[]
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        VAD_timestamp.append(frame.timestamp)
        VAD_symb=1 if is_speech else 0
        VAD_bool.append(VAD_symb)
    return np.array(VAD_bool), np.array(VAD_timestamp)

def VADBool2Segments(VAD_bool,VAD_timestamp,VAD_minlength_sample=3):
    ones_array=np.where(VAD_bool==0)[0].astype(int)
    ones_array_shift=np.roll(ones_array,-1)
    
    distance_array=ones_array_shift - ones_array
    selected_interval=np.where(distance_array>=VAD_minlength_sample)[0]
    segments=[]
    for num_i in selected_interval:
        assert (VAD_bool[ones_array[num_i]+1:ones_array[num_i+1]]==1).all()
        # print(VAD_bool[ones_array[num_i]+1:ones_array[num_i+1]])
        # print(VAD_timestamp[ones_array[num_i]+1],VAD_timestamp[ones_array[num_i+1]])
        segments.append([VAD_timestamp[ones_array[num_i]+1],VAD_timestamp[ones_array[num_i+1]]])

    return segments



def get_args():
    # we add compulsary arguments as named arguments for readability
    parser = argparse.ArgumentParser()
    parser.add_argument('--Wav_root', default='/media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata/decode_space/synced_waves_emotion44/',
                        help='minimun unit of VAD ( seconds)')
    parser.add_argument('--VADMode', default=2,
                        help='what kind of data you want to get')
    parser.add_argument('--frame_duration_ms', default=30,
                        help='what kind of data you want to get')
    parser.add_argument('--VAD_minlength', default=0.2,
                        help='minimun unit of VAD ( seconds)')
    args = parser.parse_args()
    return args
args = get_args()

frame_duration_ms=args.frame_duration_ms
VAD_minlength=args.VAD_minlength # second
VAD_minlength_sample=int(VAD_minlength/frame_duration_ms*1000) # second
vad = webrtcvad.Vad()
vad.set_mode(args.VADMode)

AllFiles=glob.glob(args.Wav_root+"*.wav")
files=[f.replace("_doc.wav","") for f in AllFiles if "_doc.wav" in f]

for file in files:
    path1=file+'_doc.wav'
    path2=file+'_kid.wav'
    audio_doc, sample_rate_doc = read_wave(path1)
    audio_kid, sample_rate_kid = read_wave(path2)
    assert sample_rate_doc == sample_rate_kid
    sample_rate=sample_rate_doc
    
    frames_doc = frame_generator(frame_duration_ms, audio_doc, sample_rate)
    frames_kid = frame_generator(frame_duration_ms, audio_kid, sample_rate)
    frames_doc = list(frames_doc)
    frames_kid = list(frames_kid)
    
    VAD_bool_doc, VAD_timestamp_doc= Get_VADBool(frames_doc)
    VAD_bool_kid, VAD_timestamp_kid=Get_VADBool(frames_kid)
    
    Segments_doc=VADBool2Segments(VAD_bool_doc, VAD_timestamp_doc,VAD_minlength_sample)
    Segments_kid=VADBool2Segments(VAD_bool_kid, VAD_timestamp_kid,VAD_minlength_sample)
    
    data_doc, rate_doc = librosa.load(path1, sr=16000)
    data_kid, rate_kid = librosa.load(path2, sr=16000)
    
    assert rate_doc == rate_kid
    rate=rate_doc
    
    data_doc = (data_doc - np.mean(data_doc)) / np.std(data_doc)
    data_kid = (data_kid - np.mean(data_kid)) / np.std(data_kid)
    
    annotation_doc=Annotate_CmpEnergy(Segments_doc,data_self=data_doc,data_other=data_kid,role='D:')
    annotation_kid=Annotate_CmpEnergy(Segments_kid,data_self=data_kid,data_other=data_doc,role='K:')
    
    annotation_sum=Annotation()
    for segment, track in annotation_doc.rename_tracks(generator='int').itertracks():
        annotation_sum[Segment(segment.start,segment.end)]="D"
    for segment, track in annotation_kid.rename_tracks(generator='int').itertracks():
        annotation_sum[Segment(segment.start,segment.end)]="K"    
    
    out_path='hype_annot_rttm/'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    out_filename=os.path.basename(path1).replace("_doc.wav","")
    suffix=".rttm"
    with open(out_path+out_filename+suffix, 'w') as f:
        annotation_sum.write_rttm(f)

    df_outAudacity=pd.DataFrame([],columns=['st','ed','symb'])
    for segment, track, label in annotation_sum.rename_tracks(generator='int').itertracks(yield_label=True):
        df_outAudacity.loc[track]=[segment.start,segment.end,label]
        # print(segment, track, label)
    out_path='hype_annot_Audacity/'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    out_filename=os.path.basename(path1).replace("_doc.wav","")
    suffix=".txt"
    df_outAudacity.to_csv(out_path+out_filename+suffix,header=None,index=False,sep='\t')


'''
這邊嘗試用pyannote做speaker diarization但是發現pretrained的model只能是設定threadshold
'''
# from pyannote.audio.features import RawAudio
# from IPython.display import Audio
# from pyannote.core import Segment, notebook

# DEMO_FILE = {'uri': 'ES2004a.Mix-Headset', 'audio': 'ES2004a.Mix-Headset.wav'}

# from pyannote.database.util import load_rttm
# groundtruth = load_rttm('MixHeadset.test.rttm')[DEMO_FILE['uri']]

# # visualize groundtruth
# groundtruth

# EXCERPT = Segment(600, 660)
# # load audio waveform, crop excerpt, and play it
# waveform = RawAudio(sample_rate=16000).crop(DEMO_FILE, EXCERPT)
# Audio(data=waveform.squeeze(), rate=16000, autoplay=True)

# import torch
# pipeline = torch.hub.load('pyannote/pyannote-audio', 'dia')
# diarization = pipeline(DEMO_FILE)



# with open('/path/to/your/audio.rttm', 'w') as f:
#     diarization.write_rttm(f)