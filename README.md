## 每一個階段都要確實做完，不能跳步
---
### 0. 影片融合以及轉檔
a. 用concat_and_compress.py把.MTS零碎的檔案都轉成一個最大的檔案 (cat_m.sh)

b. .MTS零碎的檔案都轉成.mp4 (conv_m.sh)


### 1. 影片檔（*2）與語音檔（*1）同步

a. 將影片的聲音檔摳出來（KID & DOC），我們要都在audio space擷取時間點。
*  創建一個資料夾(SyncSpace) 將醫生、小孩，的音檔和影片截出的音檔（命名為：_doc/_kid），和音檔放到這個資料夾裡面 (doc, kid 影片：使用指令Used_command.sh中的#find and transverse doc/kid mkv files to wav files。音檔使用指令： # copy and trim wav files)
*  使用Sync_FindTimestamp.py計算同步開始點 > 時間切點資料.xlsx
*  使用Gen_CutSyncScript.py > Cut_Sync.sh 然後執行
*  (optional)驗證： 再把_cut.doc.mkv, _cut.kid.mkv 的音檔和.WAV的音檔抓到SyncSpace_Post的資料夾後跑TestSync.py

### 2. 剪影片擷取ADOS其中一個活動（我們通常是取"情緒"），影片檔與語音檔都要擷取 

a. 將音檔切成每30秒鐘一段用ASR預測，找出每段音檔講emotion的部份
1.  創見資料夾decode_space然後把最原始的音檔（.WAV）都放進去
2.  使用檢查： 將切過的影片中的音檔擷取出來用聽的確認，特別注意第一句話有沒有對bash指令（#Generate data SCP file）創見data資料夾
3.  執行python create_uniform_segments.py  --window-length 10 --overlap 0  data 創造出data/segments的檔案
4.  將data丟到kaldi的資料夾，用/media/jack/workspace/560GBVolume/ADOS_data/ADOS_sound_segments/KALDI_ASR_RESULTS_FROM_SERVER/KaldiBestModel20201230的模型去decode
5.  用log/decode.*.log裡面辨識的文字去輔助你找emotion片段，然後用Audacity去找emotion開始結束的時間，手動將emotion_start/end填入時間切點資料_ManualEmotion.xlsx
6.  最後用Gen_CutSessionOffset.py去製造Cut_SyncEmotion.sh檔案然後把emotion切出來（檔案會回放原本doc/kid/audio的位置，檔案結尾會加一個_emotion的後綴）

#### 只有doc 跟kid兩個source的狀況（從2021開始的新收資料方式）
*  跟上面a. 的狀況差不多，只不過audio換成用doc的音檔。
*  檔案會有後綴 （_doc）所以在編輯excel檔的時候手動移除避免python script找不到
*  時間切點資料_ManualEmotion.xlsx 裡面audio的部份直接複製video_d的部份過去

#### 檢查： 檢查特定Session的三個source (doc, kid, audio)有沒有同步
* 將_emotion.mkv的音檔摳到SyncSpace/synced_waves(# 把emotion way 從 mkv抓下來丟到emotion)
* 將_emotion.wav的音檔也摳到SyncSpace/synced_waves(for file in $(find . -iname "*_emotion.wav");do cp $file SyncSpace/synced_waves/; done)
* 聽聽看與用眼睛看看三者有沒有同步，第一句話有沒有符合，將不符合的紀錄到
將最後計完時間資訊的excel檔留下來（手動紀錄20210506.xlsx），以及切完的_emotion,和壓縮過的合併檔案一併傳回到ftp

### 3. 標記每一句話的sentence boundary以及講那句話的人的身份（inspector/participant）

以便於後面可以同時分析inspector/participant

a. 將切過Session的音檔分開輸出成單channel的檔案後（e.g. _emotion_doc.wav _emotion_kid.wav）用SPKID_annotate.py來生成猜測的角色始末標記。
*  這邊需要灌兩個library: pyannote-core, py-webrtcvad
*    (https://github.com/pyannote/pyannote-core) (https://github.com/wiseman/py-webrtcvad)

### 4. 標記每一句話的逐字稿

#### 用ASR生逐字稿
*  用2.的方式生出data/{wav.scp, utt2spk, spk2utt, segments}，然後照著用decode.sh去解譯
*  decode完的結果用bash（# get all decoded transcripts into one file） 將需要的部份集中放到一個文字檔(finalDecodeResults.log)
*  用DecodeResultToAudacity.py將segments檔和decode結果檔整理輸出Audacity檔

#### 委外品捷逐字稿來打逐字稿
*  用utils/SegmentWavs.py 選定Audio_path 以及 Annotation_path 來根據始末標記把音檔切出來，並且生出一個utt <-> 時間的對照表：Segments_info_test_XXX.txt
>  品捷逐字稿運作方式為：提供音檔，以及utt對檔名的對照表。 他們只會把檔案裡面聽到的聲音打成逐字稿而已。因此我們需要有一個將utt還原回全音檔確切時間的機制。另外，我們每次回收檔案的時候都必須要檢查一遍
>  要確保音檔應該前後要保留一些 盡量最短要有1~2秒比較好
>  聲音太小就要自行放大給他們，至於Amplify的方式 https://www.coder.work/article/384653 提供了可以normalize音檔的方法
(接收到逐字稿後)
*  用utils/Segment_info2Audacity.py可以從Segments_info_test_XXX.txt 轉回到Audacity形式
*  搭配Audacity shortcut確認每個label， 都直接編輯在Audacity形式的文字檔annotation中
>  如果有時間線要改的話，直接更新文字檔裡面的st/ed （從audacity上面可以看到）。
>  這麼做可能utterance順序會亂掉，所以等整個檢查完就要從文字檔annotation再形成一個完整校正過的segments_info檔
*  最後，因為檢查修正的時候通常會留utterance在上面(utt: XXX)所以要使用utils/AdjustTranscripts.py來把他轉成standard transcript


#### Audacity shortcut
播放/停止：space 
重複播放： shift + space
下一個label: alt + right
