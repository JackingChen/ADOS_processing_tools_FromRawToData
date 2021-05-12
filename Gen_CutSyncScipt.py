#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 22:41:15 2020

@author: jack
"""

import os, glob
import pandas as pd
import datetime

def addSecs(tm, secs):
    
    microseconds= (secs - int(secs)) * 10e6
    
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second, tm.microsecond)
    fulldate = fulldate + datetime.timedelta(seconds=secs, microsecond=microseconds)
    return fulldate.time()

suffix='.avi'
time_info=pd.read_excel("時間切點資料.xlsx",index=None)
list_subfolders_with_paths = [root+"/"+f for root, sugdirs, files in os.walk('./') for f in files if '.avi' in f and 'output' in root]

output_path='SyncSpace/synced_waves/'
if not os.path.exists(output_path):
    os.makedirs(output_path)

with open("Cut_Sync.sh", 'w') as f:
    for i in range(len(time_info)):
        name = time_info['Unnamed: 0'][i]
        fullpaths=[s for s in list_subfolders_with_paths if os.path.basename(name) in s]
        doc_path=[s for s in fullpaths if 'doc' in s][0]
        kid_path=[s for s in fullpaths if 'kid' in s][0]
        audio_path='/'.join(doc_path.split("/")[:3]) + "/{0}.WAV".format(os.path.basename(name))
        assert os.path.exists(doc_path)
        assert os.path.exists(kid_path)
        assert os.path.exists(audio_path)
        
        out_name_audio = audio_path.replace(".WAV","_cut.WAV")
        out_name_doc= doc_path.replace(suffix,"_cut.mkv").replace("/output","")
        out_name_kid= kid_path.replace(suffix,"_cut.mkv").replace("/output","")
        
        # emotion_start=time_info['emotion_start'][i]
        # emotion_end=time_info['emotion_end'][i]
        
        # cut_start_s=emotion_start.minute * 60 + emotion_start.second + emotion_start.microsecond * 10e-7
        # emotion_end_s=emotion_end.minute * 60 + emotion_end.second + emotion_end.microsecond * 10e-7
        
        audio_offset=time_info['audio'][i]
        doctor_offset=time_info['video_d'][i]
        kid_offset=time_info['video_k'][i]
        f.write("sox {0}  -r 16k -b 16 -e signed  {2}  trim {1} \n".format(audio_path,audio_offset,out_name_audio))
        f.write("ffmpeg -i {0} -ss {1}  {2}\n".format(doc_path,doctor_offset,out_name_doc))
        f.write("ffmpeg -i {0} -ss {1}  {2}\n".format(kid_path,kid_offset,out_name_kid))
    