#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  8 18:28:05 2021

@author: jack
"""

import os, glob
import re
import pandas as pd
import csv

decode_root='decode_space/deocde_result_chichunlee'
time_info=decode_root +'/'+ "segments"
decode_content=decode_root +'/'+ "finalDecodeResults.log"
outpath='decode_space/'
outname=os.path.basename(decode_root)


df_time_info=pd.read_csv(time_info,sep=' ',header=None)
df_time_info=df_time_info.set_index(0)
df_time_info=df_time_info[[2,3]]


pattern = re.compile('-[0-9]*-[0-9]*')

with open(decode_content,"r") as fin:
    content=fin.readlines()
    for line in content:
        if len(re.findall(r'[\u4e00-\u9fff]+', line)) != 0 and 'nnet3-latgen-faster' not in line:
            utt_txts=line[line.find(":")+1:]
            utt=utt_txts.split(" ")[0]
            txts=' '.join(utt_txts.split(" ")[1:]).replace("\n","")
            df_time_info.loc[utt,'txts']=txts
        # if line.__contains__('-[0-9]*-[0-9]*'):
        #     print(line)
    # a1=re.findall('-[0-9]*-[0-9]*',content)

    
df_time_info.to_csv(outpath+outname+".txt",header=None, index=False, sep="\t", quoting=csv.QUOTE_NONE, quotechar="",  escapechar=" ")