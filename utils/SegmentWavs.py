#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 11:11:22 2019

@author: jack
"""

import json
import glob, os
import pandas as pd
from pydub import AudioSegment
from tqdm import tqdm
import re
import random
import argparse
def PreprocessCN(line):
    punc = u"-~！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.?!"
    return re.sub(u"[{}]+".format(punc), "", line)




def get_args():
    # we add compulsary arguments as named arguments for readability
    parser = argparse.ArgumentParser()
    parser.add_argument('--Audio_path', default='/media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata/decode_space/synced_waves_emotion44/',
                        help='minimun unit of VAD ( seconds)')
    parser.add_argument('--Annotation_path', default='/media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata/tmp',
                        help='what kind of data you want to get')
    parser.add_argument('--audio_padding', default=0.1,
                        help='what kind of data you want to get')
    parser.add_argument('--EXPORT_AUDIO', default=True,
                        help='minimun unit of VAD ( seconds)')

    args = parser.parse_args()
    return args
args = get_args()

#json_path='./annotation/'
#with open(json_path+"File2num_Mapping.json", 'r') as fp:
#    File2num_Mapping=json.load(fp)
EXPORT_AUDIO=args.EXPORT_AUDIO
audio_padding=args.audio_padding
#for k, v  in File2num_Mapping.items():
#    print(str(v)+".txt"+" "+k)
#Outpath_root="./Segmented_ADOS_addsil_{}/".format(audio_padding)
Outpath_root=os.getcwd() + "/../Segmented_audio/" 
if not os.path.exists(Outpath_root):
    os.makedirs(Outpath_root)
Audio_path=args.Audio_path
Annotation_path=args.Annotation_path+"/*.txt"
people=glob.glob(Annotation_path+"*")
bag=[]
Duration_bookeeping=[]
with open(os.getcwd() + "/../Segments_info_test.txt","w") as fout:
    for p in tqdm(sorted(people)):
        annotation_file=p
        name=os.path.basename(annotation_file).replace(".txt","")
        audio_file_d=Audio_path+name+'_doc.wav'
        audio_file_k=Audio_path+name+'_kid.wav'
        
        if EXPORT_AUDIO:
            Audio_d = AudioSegment.from_wav(audio_file_d)
            Audio_k = AudioSegment.from_wav(audio_file_k)
            assert len(Audio_d) == len(Audio_k)
        
        content=pd.read_csv(annotation_file,header=None, sep="\t")
        count=0
        padd_count=0
        for i in range(len(content)):
            line_info=content.iloc[i]
            st=max((line_info[0] - audio_padding),0) #for kaldi default silence top
            ed=min(line_info[1] + audio_padding,Audio_k.duration_seconds)
            st_nopadd=line_info[0] #for kaldi default silence top
            ed_nopadd=line_info[1]
            st_ms=st * 1000 #Works in milliseconds
            ed_ms=ed * 1000 #Works in milliseconds
            st_nopadd_ms=st_nopadd * 1000 #Works in milliseconds
            ed_nopadd_ms=ed_nopadd * 1000 #Works in milliseconds
            role=line_info[2].split(":")[0]
            txt=line_info[2].split(":")[1]
            txt=PreprocessCN(txt)
            bag.append([st, ed, role, txt])
            assert role in ["D","K"]
            
            if EXPORT_AUDIO:
                outfilename=name+"_"+role+"_"+str(count)+".wav"
                if role == "D":
                    if (ed_nopadd - st_nopadd) < 1: 
                        padd_count+=1
                        padd_dur=1- (ed_nopadd - st_nopadd)
                        padd_num=padd_dur*1000 / 2
                        Audio_d_segment = Audio_d[st_nopadd_ms-padd_num:ed_nopadd_ms+padd_num]
                        Duration_bookeeping.append([outfilename,Audio_d_segment.duration_seconds])
                    else:
                        Audio_d_segment = Audio_d[st_nopadd_ms:ed_nopadd_ms]
                    Audio_d_segment.export(Outpath_root+outfilename, format="wav")
                    
                elif role == "K":
                    if (ed_nopadd - st_nopadd) < 1:
                        padd_dur=1- (ed_nopadd - st_nopadd)
                        padd_num=padd_dur*1000 / 2
                        Audio_k_segment = Audio_k[st_nopadd_ms-padd_num:ed_nopadd_ms+padd_num]
                        Duration_bookeeping.append([outfilename,Audio_k_segment.duration_seconds])
                    else:
                        Audio_k_segment = Audio_k[st_nopadd_ms:ed_nopadd_ms]
                    Audio_k_segment.export(Outpath_root+outfilename, format="wav")
                    
                else:
                    assert role in ["D","K"]
            fout.write(name+"_"+role+"_"+str(count)+"\t"+str(st_nopadd)+"\t"+str(ed_nopadd)+"\t"+txt+"\t"+name+"_"+role+"\n")
            count+=1
            assert len(role) >0