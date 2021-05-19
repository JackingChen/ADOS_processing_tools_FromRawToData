#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  4 15:53:26 2021

@author: jack


音檔的命名格式請嚴格依照下列格式:
    wav format: -r 16k -b 16 -e signed 
    name: file.wav, file_doc.wav, file_kid.wav
    
這個腳本找同步時間的方式為：
    1. recover_timeshift(path1,path8) ：函數用來找path8 比path1慢多少秒才按開始
    2. 先讓audio, doc, kid三個音檔兩兩互比，找最後面的那一個(跟別人比負最多的)
    3. 以2.計算出來最快的那個為基準，計算另外兩個音檔比他慢多少
    4. 將
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
PATH='SyncSpace/sync2021'
role=['_doc','_kid']
def recover_timeshift(path1, path8):
    data1, rate1 = librosa.load(path1, sr=16000)
    data8, rate8 = librosa.load(path8, sr=16000)
    
    data1 = (data1 - np.mean(data1)) / np.std(data1)
    data8 = (data8 - np.mean(data8)) / np.std(data8)

    # print('Calculating Timeshift')
    # Find cross-correlation
    # Video8 is earlier
    xcorr = correlate(data8, data1, method='fft')
    nsamples = len(data8)
    # delta time array to match xcorr
    dt = np.arange(1-nsamples, nsamples)
    recovered_time_shift = round(dt[xcorr.argmax()] / rate1, 3)
    print('{path8} should wait {time} sec then {path1} will start'.format(path8=path8,path1=path1,time=recovered_time_shift))
    return recovered_time_shift

def DetectRole(name):
    if "_doc" in name:
        return "video_d"
    elif "_kid" in name:
        return "video_k"
    else:
        return "audio"

def get_args():
    # we add compulsary arguments as named arguments for readability
    parser = argparse.ArgumentParser()
    parser.add_argument('--NumOfSource', default=2,
                        help='what kind of data you want to get')
    
    args = parser.parse_args()
    return args

args = get_args()


files=glob.glob(PATH+"/*.wav")
print("number of input source is ",args.NumOfSource)
if args.NumOfSource==3:
    sets=sorted([s for s in files if '_doc' not in s and '_kid' not in s])
elif args.NumOfSource==2:
    sets=sorted([s.replace("_doc","") for s in files if '_doc' in s])



df_timeinfo=pd.DataFrame([],columns=['audio','video_d','video_k'])
for ss in sets:
    if args.NumOfSource == 3:
        ch1=ss
        ch2=ss.replace(".wav","_doc.wav")
        ch3=ss.replace(".wav","_kid.wav")
        channel_bag=[ch1, ch2, ch3]
    elif args.NumOfSource == 2:
        ch1=ss.replace(".wav","_doc.wav")
        ch2=ss.replace(".wav","_kid.wav")
        channel_bag=[ch1, ch2]
    comb = permutations(channel_bag, 2)
    
    #bookeep the names for outputs
    name1=os.path.basename(ch1).split(".")[0]

    
    # print([path_grp for path_grp in comb])
    # 1. find the fastest channel
    speed_bag=[]
    grp_bag=[]
    for path_grp in comb:
        path1, path8 = path_grp
        lag=recover_timeshift(path1,path8)
        grp_bag.append(path_grp)
        speed_bag.append(lag)
    fastest_channel=grp_bag[np.argmax(speed_bag)][0]
    print ("The fastest channel is",fastest_channel)
    
    # verify
    channel_bag.remove(fastest_channel)
    fastest_channel_name=os.path.basename(fastest_channel).split(".")[0]
    df_timeinfo.loc[name1,DetectRole(fastest_channel_name)]=0.0
    for ch in channel_bag:
        ch_name=os.path.basename(ch).split(".")[0]
        cut_time=recover_timeshift(fastest_channel, ch)
        print(cut_time)
        df_timeinfo.loc[name1,DetectRole(ch_name)]=cut_time


df_timeinfo.to_excel("時間切點資料_xcorr.xlsx")
        
