#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 18 11:19:52 2021

@author: jack

這個腳本用來處理ADOS Label上的： 對齊、檢查、等等事物。 目前鎖定就幾個ASD評分項目： ADOS, ADIR, CANTAB, BRIEF
來做檢查

"""

import pandas as pd
from addict import Dict
import numpy as np
label_path='/home/jack/Desktop/ADOS_label20210713_check.xlsx'
label_raw=pd.read_excel(label_path)

Otherinfo=['name', 'Module', 'int_yr',
       'int_m', 'int_d', 'site', 'family', 'id', 'sex', 'age_year',
        ]
Clinical_diagnosis=["Clinical_judgements(Autism=0 , Asperger's=1, HFA=2)"]
ADOS=['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10',
       'B11', 'B12', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9',
       'A10', 'C1', 'D1', 'D2', 'D3', 'D4', 'D5', 'E1', 'E2', 'E3']
ADIR=['adircta1', 'adircta2', 'adircta3', 'adircta4', 'adircta', 'adirctb1',
       'adirctb2', 'adirctb3', 'adirctb', 'adirctc1', 'adirctc2', 'adirctc3',
       'adirctc4', 'adirctc']
CANTAB=['MOTmL', 'PRMmcL', 'PRMcN', 'PRMcP', 'SRMmcL', 'SRMcN', 'SRMcP', 'DMSA',
       'DMSB', 'DMSmcLD', 'DMSmcLS', 'DMSpcD', 'DMSpcS', 'DMSpc0', 'DMSpc4',
       'DMSpc12', 'DMSceP', 'DMSeeP', 'DMStC', 'DMStCD', 'DMStCS', 'DMStC0',
       'DMStC4', 'DMStC12', 'PALft', 'PALmsE', 'PALmsT', 'PALcS', 'PALftS',
       'PALtE', 'PALtEA', 'PALtT', 'PALtTA', 'SSPsL', 'SSPtE', 'SSPtuE',
       'SWMbE', 'SWMbE4', 'SWMbE6', 'SWMbE8', 'SWMdE', 'SWMdE4', 'SWMdE6',
       'SWMdE8', 'SWMS', 'SWMtE', 'SWMwE', 'SWMwE4', 'SWMwE6', 'SWMwE8',
       'SOCitT2', 'SOCitT3', 'SOCitT4', 'SOCitT5', 'SOCmM2', 'SOCmM3',
       'SOCmM4', 'SOCmM5', 'SOCstT2', 'SOCstT3', 'SOCstT4', 'SOCstT5',
       'SOCpsmM', 'BLCmcL', 'BLCpC', 'BLCtC', 'BLCtE', 'IEDcsE', 'IEDcsT',
       'IEDedE', 'IEDpedE', 'IEDcS', 'IEDtE', 'IEDtEA', 'IEDtT', 'IEDtTA',
       'RTI5mT', 'RTI5rT', 'RTI1mT', 'RTI1rT', 'MTSmcL', 'MTSmeL', 'MTSmlC',
       'MTSpC', 'MTStnC', 'RVPA', 'RVPB', 'RVPmL', 'RVPfaP', 'RVPhP', 'RVPrN',
       'RVPfaN', 'RVPhN', 'RVPmN', 'SWMtE4', 'SWMtE6', 'SWMtE8', 'SOCmM',
       'SOCitT', 'SOCstT']
BRIEF=['rn_omis', 'rp_omis', 'rn_comis', 'rp_comis', 'r_rt', 'r_rtsd', 'r_var',
       'r_detect', 'r_rpsty', 'r_per', 'r_rtbc', 'r_sebc', 'r_rtisi',
       'r_seisi', 'BRI1', 'BRI2', 'BRI3', 'MI1', 'MI2', 'MI3', 'MI4', 'MI5',
       'BRI', 'MI', 'GEC']

columns=Otherinfo + Clinical_diagnosis + ADOS + ADIR + CANTAB + BRIEF

label_info=label_raw[columns]
label_info.isna().any(axis=1)

Missing_value=Dict()
for i in range(len(label_info)):
    info_person=label_info.iloc[i,:]
    missing_index=list(info_person[info_person.isna()].index)
    if info_person['Module'] == 3:
        for col in ['B11','B12','A10']:
            missing_index.remove(col)
    Missing_value[info_person['name']]=missing_index
    
MissingValuePeple=[key for key in Missing_value.keys() if len(Missing_value[key])>0]

outpath='/home/jack/Desktop/'
outfile='/home/jack/Desktop/Require_ADOSinfo_names.xlsx'

OutPutOnlymissingValPeople=False


if OutPutOnlymissingValPeople:
    label_template=pd.DataFrame()
    for name in label_raw['name']:
        if name in MissingValuePeple:
            label_template=label_template.append(label_raw[label_raw['name']==name][['int_yr','int_m', 'int_d','site', 'family', 'id']])
else:
    label_template=label_raw[['int_yr','int_m', 'int_d','site', 'family', 'id']]


for new_col in ADOS+ADIR+CANTAB+BRIEF+Clinical_diagnosis+Clinical_diagnosis:
    label_template[new_col]=None
label_template.to_excel(outfile)
