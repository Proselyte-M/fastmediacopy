import io, os
from ffmpeg import FFmpeg, Progress
import shutil


def takecareforflac(src,dst):
    temppath = os.getenv('TEMP') + str("\\") + str("pythontempfile")
    if(os.path.exists(temppath)):
        print(temppath)
    else:
        os.mkdir(temppath)
    fpath,fname = os.path.split(src)
    fname = os.path.splitext(fname)

    dpath = temppath + str("//") + fname[0] + str(".mp3")
    cover2mp3(src,dpath)
    movefile(dpath,dst)




def cutcue(CUE,PATH,dpath):
    temppath = os.getenv('TEMP') + str("\\") + str("pythontempfile")
    if(os.path.exists(temppath)):
        print(temppath)
    else:
        os.mkdir(temppath)
        
    fp = io.open(CUE,'r',encoding='utf-8')
    cue = []
    song = {}
    mediafile = ""
    for line in fp.readlines():
        text = line.strip()

        if text[:5]=='TRACK':
            song = {}
            continue

        if text[:5]=='TITLE':
            song['TITLE']= text[7:-1]
            continue
    
        if text[:9]=='PERFORMER':
            song['PERFORMER'] = text[11:-1]
            continue
    
        if text[:8]=='INDEX 01':
            song['INDEX01'] = text[9:]

        if text[:4]=='FILE':
            mediafile = text[6:-6]
            mediafile = str(PATH) + str("\\") + str(mediafile)
    
        if len(song.keys())>=3:
            cue.append(song)  
    fp.close

    line=[]
    title=[]
    for i in range(len(cue)):
        minute = int(cue[i]['INDEX01'][:2]) 
        second = int(cue[i]['INDEX01'][3:5])
        ms = int(cue[i]['INDEX01'][6:8])
        line.append((minute*60+second)+ms/1000)
        title.append(str(i + 1) + str(" - ") + cue[i]['TITLE']+'.mp3')
    
    #wav = AudioSegment.from_raw(mediafile)
    #finish=wav.duration_seconds*1000 # 增加结束点 add the finish point
    #line.append(finish)
    for i in range(len(line)):
        begin = line[i]
        if i >= len(line) - 1:
            finish = ""
        else:
            finish = line[i+1]
        outputfile = str(temppath) + str("\\") + str(title[i])
        cover2mp3WithCue(begin,finish,outputfile,mediafile)
        movefile(outputfile,dpath)




def movefile(src,dst):
    if not os.path.isfile(src):
        print("%s不存在"%src)
    else:
        fpath,fname=os.path.split(src)
        if not os.path.exists(dst):
            os.makedirs(dst)
        shutil.move(src,dst + str("\\") + fname)
        print("移动 %s --> %s"%(src,dst+ str("\\") + fname))

def copyfile(src,dst):
    if not os.path.isfile(src):
        print("%s不存在"%src)
    else:
        fpath,fname = os.path.split(src)
        if not os.path.exists(dst):
            os.makedirs(dst)
        print(shutil.copy2(src,dst + str("\\") + fname))
    
def cover2mp3WithCue(begin,finish,outputfile,mediafile):
    if finish == "":
        ffmpeg = (
    FFmpeg()
        .option("y")
        .input(mediafile)
        .output(
        outputfile,
        ab = "320k",
        map_metadata = "0",
        id3v2_version = "3",
        ss = begin,
        )
    )
    else:
        ffmpeg = (
    FFmpeg()
        .option("y")
        .input(mediafile)
        .output(
        outputfile,
        ab = "320k",
        map_metadata = "0",
        id3v2_version = "3",
        ss = begin,
        t = finish - begin
        )
    )
    @ffmpeg.on("progress")
    def on_progress(progress: Progress):
        print(progress)
    ffmpeg.execute()
    
        
def cover2mp3(src,dst):
    ffmpeg = (
     FFmpeg()
        .option("y")
        .input(src)
        .output(
        dst,
        ab = "320k",
        map_metadata = "0",
        id3v2_version = "3",
        )
     )
    @ffmpeg.on("progress")
    def on_progress(progress: Progress):
        print(progress)
    ffmpeg.execute()
    





path = "Y:\\tlmc" #扫描的目录地址
dpath = "Z:\\tlmc-opus"

for dirpath, dirnames, filenames in os.walk(path):
    lossmedialist = []
    losslessmedialist = []
    cuelist = []
    for filename in filenames:
        if os.path.splitext(filename)[-1] == ".mp3":
            lossmedialist.append(str(dirpath) + str("\\") + str(filename))
        if os.path.splitext(filename)[-1] == ".cue":
            cuelist.append(str(dirpath) + str("\\") + str(filename))
        if os.path.splitext(filename)[-1] == ".flac":
            losslessmedialist.append(str(dirpath) + str("\\") + str(filename))
        if os.path.splitext(filename)[-1] == ".wv":
            losslessmedialist.append(str(dirpath) + str("\\") + str(filename))
    '''打印列表，调试用
    for p in lossmedialist:
        print("lossmedialist",p)
    for p in losslistmedialist:
        print("losslistmedialist",p)
    for p in cuelist:
        print("cuelist",p)
    print("-------------------------------")
    '''
    dstpath = dirpath.replace(path,dpath)
    if os.path.exists(dstpath):
        print("%s 目标文件夹已存在"%(dstpath))
        continue

    for l in lossmedialist:
        copyfile(l,dstpath)
        
    if((len(cuelist) == len(losslessmedialist)) and (len(losslessmedialist) != 0)):
        #粗略判定是不是cue分轨专辑
        print("分轨专辑",dirpath)
        for c in cuelist:
            cutcue(c,dirpath,dstpath)
        continue
    
    for l in losslessmedialist:
        takecareforflac(l,dstpath)
