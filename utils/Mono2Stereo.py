#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 28 17:30:22 2021

@author: jack
"""

from pydub import AudioSegment
import os,glob
fileroot='../decode_space/synced_waves_emotion44/monowav'
outpath='../decode_space/synced_waves_emotion44/stereo'
files=glob.glob(fileroot+"/*.wav")

fileset=set(['_'.join(os.path.basename(e).split("_")[:-1]) for e in files])
for file in fileset:
    left_channel = AudioSegment.from_wav(fileroot+"/"+file+'_kid.wav')
    right_channel = AudioSegment.from_wav(fileroot+"/"+file+'_kid.wav')
    
    stereo_sound = AudioSegment.from_mono_audiosegments(left_channel, right_channel)
    stereo_sound.export(outpath+"/"+file+".wav",format="wav")
    