#  Cut Video
ffmpeg -i 2016_02_02_01_074_1.mkv -ss 0 2016_02_02_01_074_1_sync.mkv

#Generate data SCP file
train_dir=decode_wav
find $train_dir -name "*.wav" -exec sh -c 'x={}; y=$(basename -s .wav $x); printf "%s %s\n"     $y $y' \; | dos2unix > data/utt2spk
find $train_dir -name "*.wav" -exec sh -c 'x={}; y=$(basename -s .wav $x); printf "%s %s\n"     $y $y' \; | dos2unix > data/spk2utt
find $train_dir -name "*.wav" -exec sh -c 'x={}; y=$(basename -s .wav $x); printf "%s %s\n"     $y "sox $x -t wav -r 16k -b 16 -e signed - |" ' \; | dos2unix > data/wav.scp


#Decode with segment file
steps/online/nnet3/prepare_online_decoding.sh --mfcc_config conf/mfcc_hires.conf --add-pitch true data/lang exp/nnet3/extractor_formosaDAAI/ exp_DAAIKIDAug_Decept_AddADOSNoise/chain/ADOS_tdnn_fold0_transfer/ exp_DAAIKIDAug_Decept_AddADOSNoise/chain/nnet_online

#create empty frame to padd videos

ffmpeg -loop 1 -i img.jpg -t 900 -r 1 -c:v libx264 -vf scale=-2:720 blck.mp4

#find and transverse doc/kid mkv files to wav files
for file in $(find . -iname "*.mkv"); do filename=${file##*/};IFS='/' read -ra NAMES <<< "$file"; role=${NAMES[2]}; echo $role ; echo "ffmpeg -i $file  ${filename/.mkv/_${role}.wav}" ;  ; done

# 把emotion way 從 mkv抓下來丟到emotion
for file in $(find . -iname "*_emotion.mkv"); do filename=${file##*/};IFS='/' read -ra NAMES <<< "$file"; role=${NAMES[2]}; ffmpeg -i $file  ${filename/.mkv/_${role}.wav} ; done

# write inputs.txt file
printf "file '%s'\n" "$PWD/MAH00552.MP4" "$PWD/MAH00553.MP4" > inputs.txt

# concat MP3 file
ffmpeg -f concat -i inputs.txt -c copy output.mp4


