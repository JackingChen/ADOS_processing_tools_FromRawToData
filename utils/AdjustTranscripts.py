#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 17:17:07 2021

@author: jack
"""

import os,glob
import pandas as pd
import argparse

def get_args():
    # we add compulsary arguments as named arguments for readability
    parser = argparse.ArgumentParser()
    parser.add_argument('--indir', default="/media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata/Project2/transcripts_done")
    parser.add_argument('--outdir', default="/media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata/Project2/transcripts_standard")
    args = parser.parse_args()
    return args

args = get_args()

if not os.path.exists(args.outdir):
    os.makedirs(args.outdir)

files=glob.glob(args.indir+"/*.txt")

for file in files:
    name=os.path.basename(file)
    df=pd.read_csv(file,delimiter="\t",header=None)
    df_std_script=pd.DataFrame()
    std_trnscrpt_bag=[]
    for i in range(len(df)):
        trnsript=df.iloc[i][2]
        role_str=trnsript.split(":")[0]
        role= role_str.split("_")[-2]
        txt_str=trnsript.split(":")[1]
        std_trnscrpt=role+":"+txt_str
        std_trnscrpt_bag.append(std_trnscrpt)
    df_std_script=df[[0,1]]
    df_std_script[2]=std_trnscrpt_bag
    df_std_script.to_csv(args.outdir+"/"+name,header=None,index=False,sep='\t')