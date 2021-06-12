#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 20 11:52:02 2021

@author: jack
"""
import os
import numpy as np
import pandas as pd
import argparse
import glob  
from tqdm import tqdm 
from addict import Dict

def get_args():
    # we add compulsary arguments as named arguments for readability
    parser = argparse.ArgumentParser(
        description="Reads an xconfig file and creates config files "
                    "for neural net creation and training",
        epilog='Search egs/*/*/local/{nnet3,chain}/*sh for examples')
    parser.add_argument('--LMWT', default='15',
                        help='language model weight')
    parser.add_argument('--soundSegpath', default='/media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata/Project2/Segments_info_test_phase2.txt',
                        help='[/media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata/Project1/Segments_info_test_phase1.txt|]')
    parser.add_argument('--path_root', default='/media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata/SegmentInfo2Audacity/',
                        help='defaultpath')
    parser.add_argument('--trnfile', default=None,
                        help='/home/jack/Downloads/第一批_20210530_ok.xlsx|none')
    args = parser.parse_args()
    return args

args = get_args()
soundSegpath=args.soundSegpath
path_root=args.path_root
outpath=args.path_root
trnfile=args.trnfile


Global_time_info=soundSegpath
df_global_time=pd.read_csv(Global_time_info,delimiter="\t",header=None)
df_global_time.columns=['utt','st','ed','txt','role']
if trnfile:
    df_transcripts=pd.read_excel(trnfile)
    for i in range(len(df_transcripts)):
        utt=df_transcripts.iloc[i]['音檔名稱']
        txt=df_transcripts.iloc[i]['逐字稿']
        idx=df_global_time[df_global_time['utt']==utt].index[0]
        df_global_time.loc[idx,'txt']=txt


df_utt=df_global_time[['utt','txt']]


if not os.path.exists(outpath):
    os.makedirs(outpath)
suffix=".txt"

Praat_format_info_dict=Dict()

files=glob.glob(outpath+"/*.txt")
if len(files) != 0:
    os.system("rm -f " + outpath + "/*" )



df_utt.to_csv('../annotation.csv',index=False)
df_out_audacity=df_global_time[['utt','role','st','ed','txt']]
roles=[s.replace("_D","").replace("_K","") for s in df_out_audacity['role'].values]
roles_set=list(set(roles))
for role in roles_set:
    df_out=df_out_audacity[df_out_audacity['role'].str.contains(role)][['utt','role','st','ed','txt']].sort_values("st")
    for idx in df_out.index:
        # role_str= 'K:' if "_K" in df_out.loc[idx,'role'] else 'D:'
        utt_str= df_out.loc[idx,'utt'] + ":"
        df_out.loc[idx,'txt']=utt_str + df_out.loc[idx,'txt']
    outname=outpath + role + suffix
    df_out[['st','ed','txt']].to_csv(outname,header=None,sep="\t",index=False)
    