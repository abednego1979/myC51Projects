# -*- coding: UTF-8 -*-
#python 3.5

#功能1：播放MP3/WAV文件并计时，用户每按键盘就输出当前时间，用于记录音频分割点
#功能2：利用分割时间，加上一个用户输入的偏移值，分割音频文件
#sudo python3 cutAudio.py XXXX.mp3

import os
import sys
import time
import keyboard

def getTimeArray(audioFile):
    #play the audio
    print ("CWD:", os.getcwd())
    CMD='play %s &' % (audioFile)
    print ("PLAY CMD:", CMD)
    os.system(CMD)

    #
    timeArray=[]
    t=time.time()
    t=int(round(t*1000))
    timeArray.append(t)

    while True:
        if keyboard.is_pressed('a'):
            t=time.time()
            t=int(round(t*1000))
            if t-timeArray[-1]>500:
                print ("%d\t+%d" % (t, t-timeArray[-1]))
                timeArray.append(t)
        if keyboard.is_pressed('s'):
            print("timeArray=", timeArray)
            break

    Base_Time=timeArray[0]
    timeArray=[item-Base_Time for item in timeArray]

    old_item=0
    for item in timeArray:
        print ("%d\t\t+%d" % (item, item-old_item))
        old_item=item

    return timeArray

def curAudio(audioFile='', timeArrayDiff=[], timeOffset=0):
    _temp_timeArray_=[(item+timeOffset)/1000.0 for item in timeArrayDiff]

    #以_temp_timeArray_分割目标音频文件
    new_audio_list=[]
    for i in range(len(_temp_timeArray_)-1):
        print ("Start to cut %d" % (i+1))
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
    
    audioFile,=argv[:realParaNum]
    
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

main()
