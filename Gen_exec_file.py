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

time_info=pd.read_excel("時間切點資料.xlsx",index=None)




for i in range(len(time_info)):
    name = time_info['Unnamed: 0'][i]
    out_name_audio = name + '.k.wav'
    out_name_doc= "{0}/doctor/{1}_emotion.mkv".format(name,name)
    out_name_kid= "{0}/kid/{1}_emotion.mkv".format(name,name)
    emotion_start=time_info['emotion_start'][i]
    emotion_end=time_info['emotion_end'][i]
    
    emotion_start_s=emotion_start.minute * 60 + emotion_start.second + emotion_start.microsecond * 10e-7
    emotion_end_s=emotion_end.minute * 60 + emotion_end.second + emotion_end.microsecond * 10e-7
    
    doctor_offset=time_info['video_d'][i]
    kid_offset=time_info['video_k'][i]
    print("sox  {0}/{0}.WAV -r 16k -b 16 -e signed  emotion/{3}  trim {1} {2} remix 2 ".format(name,(emotion_start_s),(emotion_end_s-emotion_start_s),out_name_audio))
    print("ffmpeg -i {0}/doctor/{0}.mkv -ss {1} -to {2} {3}".format(name,(emotion_start_s+doctor_offset),(emotion_end_s+doctor_offset),out_name_doc))
    print("ffmpeg -i {0}/kid/{0}.mkv -ss {1} -to {2} {3}".format(name,(emotion_start_s+kid_offset),(emotion_end_s+kid_offset),out_name_kid))
    