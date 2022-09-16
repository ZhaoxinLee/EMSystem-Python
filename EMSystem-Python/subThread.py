import sys
import time
import pygame
from math import pi, sin, cos, sqrt, atan2, degrees,radians
from PyQt5.QtCore import pyqtSignal, QMutexLocker, QMutex, QThread
from numpy import sign

def subthreadNotDefined():
    print('Subthread not defined.')
    return

class SubThread(QThread):
    statusSignal = pyqtSignal(str)

    def __init__(self,field,vision=None,vision2=None,joystick=None,parent=None,):
        super(SubThread, self).__init__(parent)   # what is this line for Jason>>>?
        self.stopped = False
        self.mutex = QMutex()
        self.field = field
        self.vision = vision
        self.vision2 = vision2
        self.joystick = joystick
        self._subthreadName = ''
        self.params = [0,0,0,0,0]
        self.counter = 0
        self.state = None
        self.prex0 = None
        self.prey0 = None
        self.prex1 = None
        self.prey1 = None
        self.preCOMx = None
        self.preCOMy = None
        self.pretime = None
        self.mode = 0
        self.labelOnGui = {
                        'rotateXY':['Frequency (Hz)','Magniude (mT)','N/A','N/A','N/A'],
                        'rotateYZ': ['Frequency (Hz)','Magniude (mT)','N/A','N/A','N/A'],
                        'rotateXZ': ['Frequency (Hz)','Magniude (mT)','N/A','N/A','N/A'],
                        'osc_x':['Frequency(Hz)','Magnitude(mT)','HeadingAngle','N/A','N/A'],
                        'osc_z':['Frequency(Hz)','Magnitude(mT)','HeadingAngle','N/A','N/A'],
                        'joystick_test':['N/A','N/A','N/A','N/A','N/A']
                        }
        self.defaultValOnGui = {
                        'rotateXY':[1,14,0,0,0],
                        'rotateXZ':[2,2,0,0,0],
                        'rotateYZ':[3,3,0,0,0],
                        'osc_x':[1,12,0,0,0],
                        'osc_z':[1,12,0,0,0],
                        'joystick_test':[0,0,0,0,0]
                        }
        self.minOnGui = {
                        'rotateXY': [-100,0,0,0,0],
                        'rotateYZ': [-100,0,0,0,0],
                        'rotateXZ': [-100,0,0,0,0],
                        'osc_x':[-20,0,0,0,0],
                        'osc_z':[-20,0,0,0,0],
                        'joystick_test':[0,0,0,0,0]
                        }
        self.maxOnGui = {
                        'rotateXY': [100,14,0,0,0],
                        'rotateYZ': [100,14,0,0,0],
                        'rotateXZ': [100,14,0,0,0],
                        'osc_x':[20,14,360,0,0],
                        'osc_z':[20,14,360,0,0],
                        'joystick_test':[0,0,0,0,0]
                        }

    def setup(self,subThreadName):
        self._subthreadName = subThreadName
        self.stopped = False

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def run(self):
        subthreadFunction = getattr(self,self._subthreadName,subthreadNotDefined)
        subthreadFunction()

    def setParam0(self,val): self.params[0] = val
    def setParam1(self,val): self.params[1] = val
    def setParam2(self,val): self.params[2] = val
    def setParam3(self,val): self.params[3] = val
    def setParam4(self,val): self.params[4] = val

    #=========================================
    # Start defining your subthread from here
    #=========================================

    def rotateXY(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Magniude (mT)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            self.field.setFrequency(self.params[0])
            self.field.setMagnitude(self.params[1])
            theta = 2 * pi * self.params[0] * t
            fieldX = self.params[1] * cos(theta)
            fieldY = self.params[1] * sin(theta)

            self.field.setZ(0)
            self.field.setMagnitude(self.params[0])

            if self.stopped:
                return

    def rotateYZ(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Magniude (mT)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            self.field.setFrequency(self.params[0])
            self.field.setMagnitude(self.params[1])
            theta = 2 * pi * self.params[0] * t
            fieldY = self.params[1] * cos(theta)
            fieldZ = self.params[1] * sin(theta)
            self.field.setX(0)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)
            if self.stopped:
                return

    def rotateXZ(self):
        #=============================
        # reference params
        # 0 'Frequency (Hz)'
        # 1 'Magniude (mT)'
        #=============================
        startTime = time.time()
        while True:
            t = time.time() - startTime # elapsed time (sec)
            self.field.setFrequency(self.params[0])
            self.field.setMagnitude(self.params[1])
            theta = 2 * pi * self.params[0] * t
            fieldX = self.params[1] * cos(theta)
            fieldZ = self.params[1] * sin(theta)
            self.field.setX(fieldX)
            self.field.setY(0)
            self.field.setZ(fieldZ)
            if self.stopped:
                return

    def osc_x(self):
        startTime = time.time()
        while True:
            t = time.time() - startTime
            f = self.params[0]
            m = self.params[1]
            heading = self.params[2]
            self.field.setFrequency(f)
            self.field.setMagnitude(m)
            theta = 2 * pi * f * t
            # if f > 0:
            #     if sin(theta) < 0:
            #         theta = theta + pi
            # else:
            #     if sin(theta) > 0:
            #         theta = theta + pi
            fieldX = m * cosd(heading) * sin(theta)
            fieldY = m * sind(heading) * sin(theta)
            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(0)
            if self.stopped:
                return

    def osc_z(self):
        startTime = time.time()
        while True:
            t = time.time() - startTime
            f = self.params[0]
            m = self.params[1]
            heading = self.params[2]
            self.field.setFrequency(f)
            self.field.setMagnitude(m)
            theta = 2 * pi * f * t
            # if f > 0:
            #     if sin(theta) < 0:
            #         theta = theta + pi
            # else:
            #     if sin(theta) > 0:
            #         theta = theta + pi
            fieldZ = m * sin(theta)
            self.field.setX(0)
            self.field.setY(0)
            self.field.setZ(fieldZ)
            if self.stopped:
                return


    def joystick_test(self):
        startTime = time.time()
        while True:
            t = time.time() - startTime
            # joystick = pygame.joystick.Joystick(0)

            # define zig-zag direction
            if joystick.get_button(0):
                self.mode = 1
                print()
            if joystick.get_button(3):
                self.mode = 0

            mag = 14
            xCom = (mag-12.5)*joystick.get_axis(3)
            yCom = -(mag-12.5)*joystick.get_axis(4)
            fieldZ = -mag*joystick.get_axis(1)

            # zig-zag
            if joystick.get_button(9) and self.mode == 0:
                f = -3.5-2*(round(joystick.get_axis(5))+1)
                mu = 16 + 3*joystick.get_axis(2)
                md = 11 + 3*joystick.get_axis(2)+2*(-joystick.get_axis(1)+1)
                self.field.setFrequency(abs(f))
                k = f*(mu+md)
                n = t//(1/f)
                fieldZ = - md + k* (t-n/f)

            if joystick.get_button(9) and self.mode == 1:
                f = -3.5-2*(round(joystick.get_axis(5))+1)
                mu = 16 + 3*joystick.get_axis(2)
                md = 11 + 3*joystick.get_axis(2)+2*(-joystick.get_axis(1)+1)
                self.field.setFrequency(abs(f))
                k = f*(mu+md)
                n = t//(1/f)
                fieldZ = md - k* (t-n/f)

            if fieldZ > 0:
                fieldX = xCom
                fieldY = yCom
            else:
                fieldX = -xCom
                fieldY = -yCom

            self.field.setX(fieldX)
            self.field.setY(fieldY)
            self.field.setZ(fieldZ)

            if self.stopped:
                return
