#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This script only generate bash code to be exeuted 
the output of this code will be cat_m.sh, conv_m.sh
the above bash script can handle MTS files and MP4 files



update: 2021/04/30 update the code to be more readiable
"""
import subprocess


import os 
import glob

def run(Script):
    os.chdir('/media/biic/My Passport/ADOS_Data')
    for s in Script.split("\n"):
        subprocess.call(s,shell=True)
        print (s)
        

#==============================================================================
# This file is to concatenate MTS files
#==============================================================================
readpath="./"
f=open("cat_m.sh","w")
frm = open("remov_m.sh","w")
f.write("#!/bin/bash\n")
key=".MTS"
find=0

MTSfiles=glob.glob("./*/*/*/*.MTS")

sets=set(['/'.join(s.split("/")[-4:-2]) for s in MTSfiles])
roles=['doc','kid']
suffix=".MTS"

for file_root in sets:
    for role in roles:
        file_root_role=file_root+"/"+role
        files = sorted(["{0}".format(string) for string in MTSfiles if file_root_role in string])
        
        files_write_str=" ".join(files)
        
        filename=file_root.split("/")[-1]
        output_path=file_root_role+"/output"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_file=output_path+"/"+filename+suffix
        f.write("cat {input} > ./{output}\n".format(input=files_write_str\
                                                  , output=output_file))
        frm.write("rm {rmpath}/*{suffix}\n".format(rmpath=file_root_role,\
                                                  suffix=suffix))

f.close()
frm.close()           

#==============================================================================
# This file is to concatenate MP4 files
#==============================================================================
readpath="./"
f=open("cat_m.sh","a")
frm = open("remov_m.sh","a")
key=".MP4"
find=0
MP4files=glob.glob("./*/*/*/*.MP4")

sets=set(['/'.join(s.split("/")[-4:-2]) for s in MP4files])
roles=['doc','kid']
suffix=".MP4"

for file_root in sets:
    for role in roles:
        file_root_role=file_root+"/"+role
        files = sorted(["file \'{0}\'".format(os.path.basename(string)) for string in MP4files if file_root_role in string])
        
        write_str="\n".join(files)
        with open("./"+file_root+"/"+role+"/"+"inputs.txt", 'w') as finp:
            finp.write(write_str)
        filename=file_root.split("/")[-1]
        output_path=file_root_role+"/output"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_file=output_path+"/"+filename+suffix
        f.write('ffmpeg -f concat -safe 0 -i "{input}" -c copy "./{output}"\n'.format(input="./"+file_root+"/"+role+"/"+"inputs.txt"\
                                                                      , output=output_file))
        frm.write("rm {rmpath}/*{suffix}\n".format(rmpath=file_root_role,\
                                                  suffix=suffix))
f.write("exit 0")
f.close()
frm.close()    




runscript="bash ./cat_m.sh"
# subprocess.call("bash ./cat_m.sh",shell=True)

keydir = 'output'
key = '.MTS'
for root, subdirs, files in os.walk(readpath):   
    for w in files:
        if key in w and keydir in w:
            filelist = glob.glob("*.MTS")
            print (filelist)
#cat video1.mts video2.mts > whole_video.mts            





#==============================================================================
# This file is to covert Mpeg-4 files into xvid files
'''
ffmpeg -i '/media/jack/01C3EC7971227294/videos_avi/12_06_01_045/doctor/output/12_06_01_045.avi'
 -c:v mpeg4 -c:a copy -vtag xvid -qscale:v 5 '/media/jack/01C3EC7971227294/videos_avi/12_06_01_045/doctor/12_06_01_045.avi'
'''
#==============================================================================
f=open("conv_m.sh","w")
f.write("#!/bin/bash\n")

MTSfiles_merged=glob.glob("./*/*/*/output/*.MTS")

sets=set(['/'.join(s.split("/")[-5:-3]) for s in MTSfiles_merged])
roles=['doc','kid']
mergedDir='output'
suffix=".avi"

for file_root in sets:
    for role in roles:
        file_root_role=file_root+"/"+role+"/"+mergedDir
        files = sorted(["{0}".format(string) for string in MTSfiles_merged if file_root_role in string])
        
        files_write_str=" ".join(files)
        
        filename=file_root.split("/")[-1]
        output_path=file_root_role

        output_file=output_path+"/"+filename+suffix
        f.write('ffmpeg -i "{input}" -c:v mpeg4 -c:a copy -vtag xvid -qscale:v 5  "./{output}"\n'.format(input=files_write_str\
                                                  , output=output_file))


f.close()

f=open("conv_m.sh","a")
MP4files_merged=glob.glob("./*/*/*/output/*.MP4")

sets=set(['/'.join(s.split("/")[-5:-3]) for s in MP4files_merged])
roles=['doc','kid']
mergedDir='output'
suffix=".avi"

for file_root in sets:
    for role in roles:
        file_root_role=file_root+"/"+role+"/"+mergedDir
        files = sorted(["{0}".format(string) for string in MP4files_merged if file_root_role in string])
        
        files_write_str=" ".join(files)
        
        filename=file_root.split("/")[-1]
        output_path=file_root_role

        output_file=output_path+"/"+filename+suffix
        f.write('ffmpeg -i "{input}" -c:v mpeg4 -c:a copy -vtag xvid -qscale:v 5  "./{output}"\n'.format(input=files_write_str\
                                                  , output=output_file))

f.write("exit 0")
f.close()


aaa=ccc

#runscript="bash ./conv_m.sh"
#subprocess.call("bash ./conv_m.sh",shell=True)

readpath="./"
f=open("del_avi.sh","w")
f.write("#!/bin/bash\n")
key=".MTS"
find=0
for root, subdirs, files in os.walk(readpath):    
    myfiles=[]
    dir_now=root.split("/")[-1]
    outfile=root.split("/")[-2]
    if dir_now=="output":
        for w in files:
            if key in w:
                infile=os.path.join(root,w)
                outfile=os.path.join(root.replace('output',''),w.replace('avi','mkv'))
                f.write('rm '+infile.replace(")","\)").replace("(","\(")+ '\n')
#        if find!=0:        
#            f.write("cat ")
#            for words in myfiles:
#                f.write(words+" ")
#            dirpos=os.path.join(root,"output")
#            os.mkdir(dirpos)
#            outfile=os.path.join(dirpos,outfile)
#            f.write("> "+outfile+".MTS\n")
#            f.write("rm "+root+"/*.MTS\n")
        
f.write("exit 0")
f.close()    


#runscript="bash ./del_avi.sh"
#subprocess.call(runscript,shell=True)
