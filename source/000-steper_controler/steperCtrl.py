# -*- coding: utf-8 -*-

#Python 2.7.x
import time
import serial

__metaclass__ = type


class steperCtrl():
    def __init__(self):
        
        self.phase=[1,3,2,6,4,12,8,9]   #0001,0011,0010,0110,0100,1100,1000,1001
        
        self.steper0=0   #control port  P1.3,P1.2,P1.1,P1.0
        self.steper1=0   #control port  P1.7,P1.6,P1.5,P1.4
        self.steper2=0   #control port  P0.3,P0.2,P0.1,P0.0
        self.steper3=0   #control port  P0.7,P0.6,P0.5,P0.4
        self.ser=None
        self.zeroOut='00'
        return
    
    #port='COMx'
    def start(self, port, baud=9600, dsize=8, parity='N', stopbits=1):
        if port.startswith('COM'):
            self.ser = serial.Serial()
        else:
            assert 0, 'Port:'+port+' name Error.'
        self.ser.baudrate = baud
        self.ser.bytesize=dsize
        self.ser.parity=parity
        self.ser.stopbits=stopbits
        self.ser.port = int(port[len('COM')])-1
        self.ser.timeout=0.01
        
        self.ser.open()
        
        if not self.ser.isOpen():
            assert 0, 'Port:'+port+' cannot open.'
            
        self.ser.read(1000) #receive info that send by MCU init

        #reset MCU data buffer
        self.reset()
        
        #init port value
        P0='%02x' % (self.phase[self.steper2]+self.phase[self.steper3]*16)
        P1='%02x' % (self.phase[self.steper0]+self.phase[self.steper1]*16)
        
        self.beat('S0'+P0, rcvStr='S')
        self.beat('S1'+P1, rcvStr='S')
        
        self.energyCtrlDelay()
        
        self.beat('S0'+self.zeroOut, rcvStr='S')
        self.beat('S1'+self.zeroOut, rcvStr='S')
        
        return
    
    def stop(self):
        self.ser.close()
        return
    
    #host send data to mcu, must wait a while to get result
    def protocalWait(self, waitString='', waitLen=0):
        r=''
        if waitLen<=0:
            while True:
                r+=self.ser.read(10)
                if r.startswith(waitString):
                    break
        else:
            while True:
                r+=self.ser.read(10)
                if len(r)>=waitLen:
                    break
        return r
    
    #to reduce the energy consume, we set steper and set steper to no electric current after the steper has been stable.
    #this func is to wait the steper get stable
    def energyCtrlDelay(self):
        time.sleep(0.2)
        return
    
    def beat(self, snd, rcvStr='', rcvlen=0):
        self.ser.write(snd)
        r=self.protocalWait(rcvStr, rcvlen)        
        return r
    
    def step(self, x=0, y=0, z=0, w=0):
        assert x==0 or x==1 or x==-1
        assert y==0 or y==1 or y==-1
        assert z==0 or z==1 or z==-1
        assert w==0 or w==1 or w==-1
        
        #update steper0
        temp = self.steper0+x
        if temp<0:
            temp+=len(self.phase)
        if temp>=len(self.phase):
            temp-=len(self.phase)
        self.steper0=temp
        
        #update steper1
        temp = self.steper1+x
        if temp<0:
            temp+=len(self.phase)
        if temp>=len(self.phase):
            temp-=len(self.phase)
        self.steper1=temp
        
        #update steper2
        temp = self.steper2+x
        if temp<0:
            temp+=len(self.phase)
        if temp>=len(self.phase):
            temp-=len(self.phase)
        self.steper2=temp    
        
        #update steper3
        temp = self.steper3+x
        if temp<0:
            temp+=len(self.phase)
        if temp>=len(self.phase):
            temp-=len(self.phase)
        self.steper3=temp 
        
        P0='%02x' % (self.phase[self.steper2]+self.phase[self.steper3]*16)
        P1='%02x' % (self.phase[self.steper0]+self.phase[self.steper1]*16)        

        self.beat('S0'+P0, rcvStr='S')
        self.beat('S1'+P1, rcvStr='S')

        self.energyCtrlDelay()
    
        self.beat('S0'+self.zeroOut, rcvStr='S')
        self.beat('S1'+self.zeroOut, rcvStr='S')

        return
    
    def sensor(self):
        r=self.beat('G2', rcvlen=3)
        
        assert r.startswith('G')

        value=int('0x'+r[1:], 16)
        return value
    
    def reset(self):
        self.beat('X', rcvStr='RESET')
        return
        
    
    
sc=steperCtrl()
sc.start('COM4')
for i in range(100):
    sc.step(1,1,1,1)
sc.reset()
sc.stop()