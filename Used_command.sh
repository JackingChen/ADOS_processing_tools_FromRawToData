#  Cut Video
ffmpeg -i 2016_02_02_01_074_1.avi -ss 0 2016_02_02_01_074_1_sync.avi

#Generate data SCP file
mkdir -p data
train_dir=decode_space
find $train_dir -name "*.wav" -exec sh -c 'x="{}"; y=$(basename -s .wav $x); printf "%s %s\n"     $y $y' \; | dos2unix > data/utt2spk
find $train_dir -name "*.wav" -exec sh -c 'x="{}"; y=$(basename -s .wav $x); printf "%s %s\n"     $y $y' \; | dos2unix > data/spk2utt
find $train_dir -name "*.wav" -exec sh -c 'x="{}"; y=$(basename -s .wav $x); printf "%s %s\n"     $y "sox \"$PWD/$x\" -t wav -r 16k -b 16 -e signed - remix 1 |" ' \; | dos2unix > data/wav.scp


#Decode with segment file
steps/online/nnet3/prepare_online_decoding.sh --mfcc_config conf/mfcc_hires.conf --add-pitch true data/lang exp/nnet3/extractor_formosaDAAI/ exp_DAAIKIDAug_Decept_AddADOSNoise/chain/ADOS_tdnn_fold0_transfer/ exp_DAAIKIDAug_Decept_AddADOSNoise/chain/nnet_online

#create empty frame to padd videos

ffmpeg -loop 1 -i img.jpg -t 900 -r 1 -c:v libx264 -vf scale=-2:720 blck.mp4

#find and transverse doc/kid mkv files to wav files
#for file in $(find . -iname "*.avi"); do filename=${file##*/};IFS='/' read -ra NAMES <<< "$file"; role=${NAMES[2]}; echo $role ; echo "ffmpeg -i $file  ${filename/.avi/_${role}.wav}" ;  done
for file in $(find . -iname "*.avi"); do filename=${file##*/};IFS='/' read -ra NAMES <<< "$file"; role=${NAMES[3]}; echo $role ; echo "ffmpeg -i '$file' -vn -ac 1 -ar 16000 -ss 0.0 -to 300 'SyncSpace/${filename/.avi/_${role}.wav}'" ;  done > Extrat4Sync.sh

# 抓.WAV但是不抓_cut.WAV
find . -name "*.WAV" -not -path "*_cut*" -exec bash -c 'x={};name=$(basename $x);cp  $x decode_space/$name'  \;


# 把emotion way 從 mkv抓下來丟到emotion
#for file in $(find . -iname "*_emotion.avi"); do filename=${file##*/};IFS='/' read -ra NAMES <<< "$file"; role=${NAMES[2]}; ffmpeg -i $file  ${filename/.avi/_${role}.wav} ; done
for file in $(find . -iname "*_emotion.mkv"); do filename=${file##*/};IFS='/' read -ra NAMES <<< "$file"; role=${NAMES[3]}; ffmpeg -i $file -vn -ac 1 -ar 16000  "SyncSpace/synced_waves/${filename/.mkv/_${role}.wav}" ; done

# write inputs.txt file
printf "file '%s'\n" "$PWD/MAH00552.MP4" "$PWD/MAH00553.MP4" > inputs.txt

# concat MP3 file
ffmpeg -f concat -i inputs.txt -c copy output.mp4

# copy and trim wav files
# navigate to /media/jack/workspace/560GBVolume/ados_processing_tools_fromrawtodata
# 有些影片聲音開始時間會差超過1分鐘，乾脆直接用5分鐘
find . -maxdepth 3 -name "*.WAV" -exec bash -c 'x={};name=$(basename $x); echo "sox $x -r 16k -b 16 -e signed SyncSpace/sync2020/$name trim 0 300 remix 1"' \;

# format all audios to standard formats
find . -iname "*.wav" -exec bash -c 'x={}; sox $x -r 16k -e signed ${x}_tmp.wav remix 1; mv ${x}_tmp.wav ${x}' \;


# In path: decode_ADOS_tdnn_fold_transfer/log 
# get all decoded transcripts into one file
# grep "[\p{Han}]"  ./decode.*.log > finalDecodeResults.log
grep "^[0-9]*_[0-9]*_[0-9]*_[0-9]*"  ./decode.*.log  > finalDecodeResults.log
