# -*- coding: UTF-8 -*-
#python 3.5

#功能1：播放MP3/WAV文件并计时，用户每按键盘就输出当前时间，用于记录音频分割点
#功能2：利用分割时间，加上一个用户输入的偏移值，分割音频文件


import os
import sys
import time
import keyboard

def getTimeArray(audioFile):
    #play the audio
    os.system('play %s &' % (audioFile))

    #
    timeArray=[]
    t=time.time()
    t=int(round(t*1000))
    timeArray.append(t)
    
    while True:
        if keyboard.is_pressed('a'):
            t=time.time()
            t=int(round(t*1000))
            timeArray.append(t)
            print (t)
            time.sleep(0.2)
        if keyboard.is_pressed('s'):
            print("timeArray=", timeArray)
            break
    
    timeArrayDiff=[]
    for i in range(len(timeArray)):
        if i==0:
            timeArrayDiff.append(0)
            continue
        else:
            timeArrayDiff.append(timeArray[i]-timeArray[i-1])
    
    print("timeArrayDiff=", timeArrayDiff)
    return timeArrayDiff

def curAudio(audioFile='', timeArrayDiff=[], timeOffset=0):
    _temp_timeArray_=[(item+timeOffset)/1000.0 for item in timeArrayDiff]
    
    #以_temp_timeArray_分割目标音频文件
    new_audio_list=[]
    for i in range(len(_temp_timeArray_)-1):
        #startTime=_temp_timeArray_[i]
        #endTime=_temp_timeArray_[i+1]
        _temp0_,_temp1_=os.path.splitext(audioFile)
        _temp_new_audio_="%s_%03d%s" % (_temp0_, i+1, _temp1_)
        new_audio_list.append(_temp_new_audio_)
        os.system('sox %s %s trim %f =%f' % (audioFile, _temp_new_audio_, _temp_timeArray_[i], _temp_timeArray_[i+1]))
    
    #分割以后以明显的间隔播放文件，让使用者判断是否分割正确
    for _temp_new_audio_ in new_audio_list:
        os.system('play %s' % (_temp_new_audio_))
        time.sleep(2)
    
    return

def main():
    argv = sys.argv
    argv = argv[1:]
    realParaNum=1
    if len(argv) < realParaNum:
        print ("Paras:", argv)
        assert 0
        sys.exit(1)
    
    audioFile=argv[:realParaNum]
    
    timeArrayDiff=[]
    
    
    while True:
        a=input("Start to set cut point of Audio File, Press any key to Start...:")
        timeArrayDiff = getTimeArray(audioFile)
        a=input("Get cut point again?(y to cur again):")
        if a=='y' or a=='Y':
            continue
        else:
            break
    
    timeOffset=0
    while True:
        a=input("Input time offset to cut audio (ms):")
        curAudio(audioFile, timeArrayDiff, timeOffset)
        a=input("Cut audio again?(y to cur again):")
        if a=='y' or a=='Y':
            continue
        else:
            break
    pass

if __name__ == "__name__":
    main()
