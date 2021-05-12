#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  6 16:35:09 2021

@author: jack

這個腳本計算emotion start 和emotion end 在扣掉Sync的時間點後的時間，並且output一個post的emotion start/end 在時間切點資料_CutOffset.xlsx

"""

import os, glob
import pandas as pd
import datetime
import argparse
def get_args():
    # we add compulsary arguments as named arguments for readability
    parser = argparse.ArgumentParser()
    parser.add_argument('--NumOfSource', default=2,
                        help='what kind of data you want to get')
    
    args = parser.parse_args()
    return args

args = get_args()

def addSecs(tm, secs):
    
    microseconds= (secs - int(secs)) * 10e6
    
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second, tm.microsecond)
    fulldate = fulldate + datetime.timedelta(seconds=secs, microsecond=microseconds)
    return fulldate.time()

suffix='.avi'
time_info=pd.read_excel("時間切點資料_ManualEmotion.xlsx",index=None)
list_subfolders_with_paths = [root+"/"+f for root, sugdirs, files in os.walk('./') for f in files if '.avi' in f and 'output' in root]


for i in range(len(time_info)):
    time_info.loc[i,'doc_v-audio']=time_info.loc[i,'video_d'] - time_info.loc[i,'audio']
    time_info.loc[i,'kid_v-audio']=time_info.loc[i,'video_k'] - time_info.loc[i,'audio']
    time_info.loc[i,'emotion_start_d']=time_info.loc[i,'emotion_start_audio'] + time_info.loc[i,'doc_v-audio']
    time_info.loc[i,'emotion_start_k']=time_info.loc[i,'emotion_start_audio'] + time_info.loc[i,'kid_v-audio']
    time_info.loc[i,'emotion_end_d']=time_info.loc[i,'emotion_end_audio'] + time_info.loc[i,'doc_v-audio']
    time_info.loc[i,'emotion_end_k']=time_info.loc[i,'emotion_end_audio'] + time_info.loc[i,'kid_v-audio']
time_info.to_excel('時間切點資料_CutOffset.xlsx')


with open("Cut_SyncEmotion.sh", 'w') as f:
    for i in range(len(time_info)):
        name = time_info['Unnamed: 0'][i]
        fullpaths=[s for s in list_subfolders_with_paths if os.path.basename(name) in s]
        doc_path=[s for s in fullpaths if 'doc' in s][0]
        kid_path=[s for s in fullpaths if 'kid' in s][0]
        
        if args.NumOfSource ==3:
            audio_path='/'.join(doc_path.split("/")[:3]) + "/{0}.WAV".format(os.path.basename(name))
        elif args.NumOfSource ==2:
            audio_path=doc_path
            
        
        assert os.path.exists(doc_path)
        assert os.path.exists(kid_path)
        assert os.path.exists(audio_path)
        out_name_audio = audio_path.replace(".WAV","_emotion.wav")
        out_name_doc= doc_path.replace(suffix,"_emotion.mkv").replace("/output","")
        out_name_kid= kid_path.replace(suffix,"_emotion.mkv").replace("/output","")
        
        emotion_start_audio=time_info['emotion_start_audio'][i]
        emotion_end_audio=time_info['emotion_end_audio'][i]
        emotion_start_d=time_info['emotion_start_d'][i]
        emotion_start_k=time_info['emotion_start_k'][i]
        emotion_end_d=time_info['emotion_end_d'][i]
        emotion_end_k=time_info['emotion_end_k'][i]
        
        # emotion_start_s=emotion_start.minute * 60 + emotion_start.second + emotion_start.microsecond * 10e-7
        # emotion_end_s=emotion_end.minute * 60 + emotion_end.second + emotion_end.microsecond * 10e-7
        
        doctor_offset=time_info['video_d'][i]
        kid_offset=time_info['video_k'][i]
        if args.NumOfSource ==3:
            f.write("sox  {0} -r 16k -b 16 -e signed  {3}  trim {1} {2}  \n".format(audio_path,emotion_start_audio,(emotion_end_audio-emotion_start_audio),out_name_audio))
        f.write("ffmpeg -i '{0}' -ss {1} -to {2} '{3}'\n".format(doc_path,emotion_start_d,emotion_end_d,out_name_doc))
        f.write("ffmpeg -i '{0}' -ss {1} -to {2} '{3}'\n".format(kid_path,emotion_start_k,emotion_end_k,out_name_kid))
    