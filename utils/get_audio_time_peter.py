#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 22:21:21 2020

@author: crowpeter
"""
import glob
import os, sys
import soundfile as sf
root_path=sys.argv[1]
database_name_list=['']

# total_time = 0
# total_utt_num = 0
for database_name in database_name_list:
    total_time = 0
    total_utt_num = 0
    print(database_name)
    for dirPath, dirNames, txtsNames in os.walk(root_path):
        if len(txtsNames) != 0 and '.wav' in txtsNames[0]:
            for wav_dir in txtsNames:

                s, fs = sf.read(os.path.join(dirPath,wav_dir))
                total_time = total_time + s.shape[0]/fs
                total_utt_num += 1
                
                if database_name == 'DaAi[16k][16bit]':
                    if s.shape == 1:
                        with open(database_name+'_no_two_ch','a') as f:
                            f.write(os.path.join(dirPath,wav_dir)+'\n')
    # print(database_name)
    print('total_time:' + str(total_time))
    print('total_utt_num:' + str(total_utt_num))
    print('average_time:' + str(total_time/total_utt_num))
