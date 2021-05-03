train_dir=decode_wav
find $train_dir -name "*.wav" -exec sh -c 'x={}; y=$(basename -s .wav $x); printf "%s %s\n"     $y $y' \; | dos2unix > data/utt2spk
find $train_dir -name "*.wav" -exec sh -c 'x={}; y=$(basename -s .wav $x); printf "%s %s\n"     $y $y' \; | dos2unix > data/spk2utt
find $train_dir -name "*.wav" -exec sh -c 'x={}; y=$(basename -s .wav $x); printf "%s %s\n"     $y "sox -t wav $PWD/$x -t wav -r 16k -b 16 -e signed -c 1 - |" ' \; | dos2unix > data/wav.scp

