import sys
import time
from math import pi, sin, cos, sqrt, atan2, degrees,radians
from PyQt5.QtCore import pyqtSignal, QMutexLocker, QMutex, QThread
from numpy import sign
import pygame

def subthreadNotDefined():
    print('Subthread not defined.')
    return

def cosd(val):
    return cos(radians(val))

def sind(val):
    return sin(radians(val))

class SubThread(QThread):
    statusSignal = pyqtSignal(str)

    def __init__(self,field,vision=None,vision2=None,joystick=None,parent=None):
        super(SubThread, self).__init__(parent)
        self.stopped = False
        self.mutex = QMutex()
        self.field = field
        self.vision = vision
        self.vision2 = vision2
        self.joystick = joystick
        self._subthreadName = ''
        self.params = [0,0,0,0,0]
        self.counter = 0
        self.js_rolling_state = 0
        self.prex0 = None
        self.prey0 = None
        self.prex1 = None
        self.prey1 = None
        self.preCOMx = None
        self.preCOMy = None
        self.pretime = None
        self.mode = 0
        self.labelOnGui = {
                        'default':['param0','param1','param2','param3','param4'],
                        'rotateXY':['Frequency (Hz)','Magniude (mT)','N/A','N/A','N/A'],
                        'rotateYZ': ['Frequency (Hz)','Magniude (mT)','N/A','N/A','N/A'],
                        'rotateXZ': ['Frequency (Hz)','Magniude (mT)','N/A','N/A','N/A'],
                        'oscXYZ':['Frequency(Hz)','Magnitude(mT)','AzimuthalAngle','TiltingAngle','N/A'],
                        'oscXYZ_tophemi':['Frequency(Hz)','Magnitude(mT)','AzimuthalAngle','TiltingAngle','N/A'],
                        'joystick_uniform':['N/A','N/A','N/A','N/A','N/A'],
                        'joystick_rolling':['N/A','N/A','N/A','N/A','N/A'],
                        'joystick_rotating':['N/A','N/A','N/A','N/A','N/A'],
                        'joystick_crawling':['N/A','N/A','N/A','N/A','N/A']
                        }
        self.defaultValOnGui = {
                        'default':[0,0,0,0,0],
                        'rotateXY':[1,14,0,0,0],
                        'rotateXZ':[2,2,0,0,0],
                        'rotateYZ':[10,16,0,0,0],
                        'oscXYZ':[1,12,0,0,0],
                        'oscXYZ_tophemi':[1,12,0,0,0],
                        'joystick_uniform':[0,0,0,0,0],
                        'joystick_rolling':[0,0,0,0,0],
                        'joystick_rotating':[0,0,0,0,0],
                        'joystick_crawling':[0,0,0,0,0]
                        }
        self.minOnGui = {
                        'default':[0,0,0,0,0],
                        'rotateXY': [-100,0,0,0,0],
                        'rotateYZ': [-100,0,0,0,0],
                        'rotateXZ': [-100,0,0,0,0],
                        'oscXYZ':[-20,0,0,-90,0],
                        'oscXYZ_tophemi':[-20,0,0,0,0],
                        'joystick_uniform':[0,0,0,0,0],
                        'joystick_rolling':[0,0,0,0,0],
                        'joystick_rotating':[0,0,0,0,0],
                        'joystick_crawling':[0,0,0,0,0]
                        }
        self.maxOnGui = {
                        'default':[0,0,0,0,0],
                        'rotateXY': [100,25,0,0,0],
                        'rotateYZ': [100,25,0,0,0],
                        'rotateXZ': [100,25,0,0,0],
                        'oscXYZ':[20,25,360,90,0],
                        'oscXYZ_tophemi':[20,14,360,90,0],
                        'joystick_uniform':[0,0,0,0,0],
                        'joystick_rolling':[0,0,0,0,0],
                        'joystick_rotating':[0,0,0,0,0],
                        'joystick_crawling':[0,0,0,0,0]
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
            self.field.B_Global_Desired[0] = fieldX/1000 # mT -> T
            self.field.B_Global_Desired[1] = fieldY/1000 # mT -> T
            self.field.B_Global_Desired[2] = 0
            self.field.setXYZ(self.field.B_Global_Desired)
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
            self.field.B_Global_Desired[0] = 0
            self.field.B_Global_Desired[1] = fieldY/1000 # mT -> T
            self.field.B_Global_Desired[2] = fieldZ/1000 # mT -> T
            self.field.setXYZ(self.field.B_Global_Desired)
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
            self.field.B_Global_Desired[0] = fieldX/1000 # mT -> T
            self.field.B_Global_Desired[1] = 0
            self.field.B_Global_Desired[2] = fieldZ/1000 # mT -> T
            self.field.setXYZ(self.field.B_Global_Desired)
            if self.stopped:
                return

    def oscXYZ(self): # sinusoidal oscillating field in 3D, you can regard the field vector pointing to the surface of a sphere with varying radius
        startTime = time.time()
        while True:
            t = time.time() - startTime
            f = self.params[0]
            m = self.params[1] # magnitude of the field, equivalent to the radius of the sphere
            azimuthal = self.params[2] # default is pointing towards +x, increasing along +z axis
            tilting = self.params[3]# default is pointing towards +x, increasing along -y axis
            self.field.setFrequency(f)
            self.field.setMagnitude(m)
            theta = 2 * pi * f * t
            fieldX = m * sin(theta) * cosd(tilting) * cosd(azimuthal)
            fieldY = m * sin(theta) * cosd(tilting) * sind(azimuthal)
            fieldZ = m * sin(theta) * sind(tilting)
            self.field.B_Global_Desired[0] = fieldX/1000 # mT -> T
            self.field.B_Global_Desired[1] = fieldY/1000 # mT -> T
            self.field.B_Global_Desired[2] = fieldZ/1000 # mT -> T
            self.field.setXYZ(self.field.B_Global_Desired)
            if self.stopped:
                return

    def oscXYZ_tophemi(self): # sinusoidal oscillating field in 3D space above XY plane, you can regard the field vector pointing to the surface of a hemisphere with varying radius
        startTime = time.time()
        while True:
            t = time.time() - startTime
            f = self.params[0]
            m = self.params[1] # magnitude of the field, equivalent to the radius of the hemisphere
            azimuthal = self.params[2] # default is pointing towards +x, increasing along +z axis
            tilting = self.params[3]# default is pointing towards +x, increasing along -y axis
            self.field.setFrequency(f)
            self.field.setMagnitude(m)
            theta = 2 * pi * f * t
            fieldX = m * sin(theta) * cosd(tilting) * cosd(azimuthal)
            fieldY = m * sin(theta) * cosd(tilting) * sind(azimuthal)
            fieldZ = m * abs(sin(theta)) * sind(tilting)
            self.field.B_Global_Desired[0] = fieldX/1000 # mT -> T
            self.field.B_Global_Desired[1] = fieldY/1000 # mT -> T
            self.field.B_Global_Desired[2] = fieldZ/1000 # mT -> T
            self.field.setXYZ(self.field.B_Global_Desired)
            if self.stopped:
                return


    def joystick_uniform(self): # general control of field x,y,z using joystick
        startTime = time.time()
        while True:
            t = time.time() - startTime

            if self.joystick != None:
                maxField = 20 # absolute value of maximum field
                self.field.B_Global_Desired[0] = self.joystick.get_axis(0)*maxField/1000 # field X, Left X-axis
                self.field.B_Global_Desired[1] = -self.joystick.get_axis(1)*maxField/1000 # field Y, Left Y-axis
                self.field.B_Global_Desired[2] = -self.joystick.get_axis(3)*maxField/1000 # field Z, Left Y-axis
                self.field.setXYZ(self.field.B_Global_Desired)
            else:
                return

            if self.stopped:
                return

    def joystick_rolling(self):
        startTime = time.time()
        while True:
            t = time.time() - startTime

            if self.joystick.get_button(1):
                self.js_rolling_state = 1 # press button B for rolling control
            elif self.joystick.get_button(0):
                self.js_rolling_state = 0 # press button A for opening and closing control

            # opening and closing control
            if self.js_rolling_state == 0:
                if sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2) >= 0.2: # general control
                    maxField = 25 # absolute value of maximum field
                    Bx = self.joystick.get_axis(0)*maxField/1000 # field X, Left X-axis
                    By = -self.joystick.get_axis(1)*maxField/1000 # field Y, Left Y-axis
                    if self.joystick.get_axis(5) > -0.5:
                        Bz = 10*(self.joystick.get_axis(5)+1)/1000
                    elif self.joystick.get_axis(4) > -0.5:
                        Bz = -10*(self.joystick.get_axis(4)+1)/1000
                    else:
                        Bz = 0
                    fieldX = Bx # field X, Left X-axis
                    fieldY = By # field Y, Left Y-axis
                    fieldZ = Bz
                else:
                    fieldX = 0
                    fieldY = 0
                    fieldZ = 0

            # rolling control
            if self.js_rolling_state == 1:
                XRoll = self.joystick.get_axis(2) # Rolling along x axis, Right X-axis
                YRoll = -self.joystick.get_axis(3) # Rolling along y axis, Right Y-axis
                inplaneMag = sqrt(XRoll**2+YRoll**2) # in-plane component of field magnitude
                freq = 1*round(self.joystick.get_axis(5)+2) # rolling frequency, R2
                Mag = 3*round(-self.joystick.get_axis(1)+2)  # rolling magnitude, L2
                theta = 2 * pi * freq * t
                if inplaneMag >= 0.2:
                    fieldX = -Mag * cos(theta) * XRoll/inplaneMag /1000
                    fieldY = -Mag * cos(theta) * YRoll/inplaneMag /1000
                    fieldZ = Mag * sin(theta) /1000

            self.field.B_Global_Desired[0] = fieldX
            self.field.B_Global_Desired[1] = fieldY
            self.field.B_Global_Desired[2] = fieldZ
            self.field.setXYZ(self.field.B_Global_Desired)


            if self.stopped:
                return

    def joystick_rotating(self): # in-plane rotation with user-defined azimuthal angle
        startTime = time.time()
        while True:
            t = time.time() - startTime
            XRoll = self.joystick.get_axis(2) # Rolling along x axis, Right X-axis
            YRoll = -self.joystick.get_axis(3) # Rolling along y axis, Right Y-axis
            inplaneMag = sqrt(XRoll**2+YRoll**2) # in-plane component of field magnitude
            freq = 12
            Mag = 16
            theta = 2 * pi * freq * t
            if inplaneMag >= 0.2:
                fieldY = Mag * cos(theta) * XRoll/inplaneMag /1000 # this direction is for helical robot actuation, which is perpendicular to the rotational plane, see commented lines below for rotational plane
                fieldX = -Mag * cos(theta) * YRoll/inplaneMag /1000
                # fieldX = -Mag * cos(theta) * XRoll/inplaneMag /1000 # this is within the rotational plane
                # fieldY = -Mag * cos(theta) * YRoll/inplaneMag /1000
                fieldZ = Mag * sin(theta) /1000
            else:
                fieldX = 0
                fieldY = 0
                fieldZ = 0

            self.field.B_Global_Desired[0] = fieldX
            self.field.B_Global_Desired[1] = fieldY
            self.field.B_Global_Desired[2] = fieldZ
            self.field.setXYZ(self.field.B_Global_Desired)
            if self.stopped:
                return

    def joystick_crawling(self): # square signal for walking robot actuation
        startTime = time.time()
        while True:
            t = time.time() - startTime
            X = self.joystick.get_axis(2)
            Y = -self.joystick.get_axis(3)
            Z = -self.joystick.get_axis(1)
            inplaneMag = sqrt(X**2+Y**2) # in-plane component of field magnitude
            MagY = 25*Y
            MagZ = Z*15
            if inplaneMag >= 0.2:
                # if X >= 0:
                #     fieldX = Mag /1000
                # else:
                #     fieldX = -Mag /1000
                fieldX-0
                fieldY = MagY /1000
                fieldZ = MagZ /1000
            else:
                fieldX = 0
                fieldY = 0
                fieldZ = 0

            self.field.B_Global_Desired[0] = fieldX
            self.field.B_Global_Desired[1] = fieldY
            self.field.B_Global_Desired[2] = fieldZ
            self.field.setXYZ(self.field.B_Global_Desired)
            if self.stopped:
                return
# joystick button and axis definition, always commented
#          KEY = {
#         'A': 0,
#         'B': 1,
#         'X': 2,
#         'Y': 3,
#         'LTOP': 4,
#         'RTOP': 5,
#         'BACK': 6,
#         'START': 7,
#         'HOME': 8,
#         'TOP_LEFT': 9,
#         'BOT_RIGHT': 10,
#         }
#         AXIS = {
#             'L_X': 0,
#             'L_Y': 1,
#             'L_BACK': 2,
#             'R_X': 3,
#             'R_Y': 4,
#             'R_BACK': 5
#         }
