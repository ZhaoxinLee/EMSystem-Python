import sys
import time
from math import pi, sin, cos, sqrt, atan2, degrees, radians, asin, acos
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
                        'joystick_crawling':['N/A','N/A','N/A','N/A','N/A'],
                        'wrist_gripper':['tilting','N/A','N/A','N/A','N/A'],
                        'wrist_gripper_vertical':['tilting','N/A','N/A','N/A','N/A'],
                        'cutting':['N/A','N/A','N/A','N/A','N/A']
                        }
        self.defaultValOnGui = {
                        'default':[0,0,0,0,0],
                        'rotateXY':[1,14,0,0,0],
                        'rotateXZ':[2,2,0,0,0],
                        'rotateYZ':[10,16,0,0,0],
                        'oscXYZ':[1,12,0,0,0],
                        'oscXYZ_tophemi':[1,20,90,0,0],
                        'joystick_uniform':[0,0,0,0,0],
                        'joystick_rolling':[0,0,0,0,0],
                        'joystick_rotating':[0,0,0,0,0],
                        'joystick_crawling':[0,0,0,0,0],
                        'wrist_gripper':[0,0,0,0,0],
                        'wrist_gripper_vertical':[0,0,0,0,0],
                        'cutting':[0,0,0,0,0]
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
                        'joystick_crawling':[0,0,0,0,0],
                        'wrist_gripper':[0,0,0,0,0],
                        'wrist_gripper_vertical':[-90,0,0,0,0],
                        'cutting':[0,0,0,0,0]
                        }
        self.maxOnGui = {
                        'default':[0,0,0,0,0],
                        'rotateXY': [100,25,0,0,0],
                        'rotateYZ': [100,25,0,0,0],
                        'rotateXZ': [100,25,0,0,0],
                        'oscXYZ':[20,25,360,90,0],
                        'oscXYZ_tophemi':[20,25,360,90,0],
                        'joystick_uniform':[0,0,0,0,0],
                        'joystick_rolling':[0,0,0,0,0],
                        'joystick_rotating':[0,0,0,0,0],
                        'joystick_crawling':[0,0,0,0,0],
                        'wrist_gripper':[90,0,0,0,0],
                        'wrist_gripper_vertical':[90,0,0,0,0],
                        'cutting':[0,0,0,0,0]
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
            n = self.params[3]# default is pointing towards +x, increasing along -y axis
            self.field.setFrequency(f)
            self.field.setMagnitude(m)
            theta = 2 * pi * f * t
            fieldX = m * sin(theta) * cosd(azimuthal)
            fieldY = m * sin(theta) * sind(azimuthal)

            if fieldY < -15:
                fieldZ = -n * abs(sin(theta))
            elif fieldY > 15:
                fieldZ = -(10-n) * abs(sin(theta))
            else:
                fieldZ = 0

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
                if abs(self.joystick.get_axis(0))>=0.2:
                    self.field.B_Global_Desired[0] = self.joystick.get_axis(0)*maxField/1000 # field X, Left X-axis
                else:
                    self.field.B_Global_Desired[0] = 0
                if abs(self.joystick.get_axis(3))>=0.2:
                    self.field.B_Global_Desired[1] = -self.joystick.get_axis(3)*maxField/1000 # field Y, Right Y-axis
                else:
                    self.field.B_Global_Desired[1] = 0
                if self.joystick.get_axis(4)>0:
                    self.field.B_Global_Desired[2] = -(self.joystick.get_axis(4))*maxField/1000 # negative field Z, Left back
                elif self.joystick.get_axis(5)>0:
                    self.field.B_Global_Desired[2] = (self.joystick.get_axis(5))*maxField/1000 # positive field Z, Right back
                else:
                    self.field.B_Global_Desired[2] = 0
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
                Mag = 8*round(-self.joystick.get_axis(1)+2)#3*round(-self.joystick.get_axis(1)+2)  # rolling magnitude, L2
                theta = 2 * pi * freq * t
                if inplaneMag >= 0.3:
                    fieldX = -Mag * cos(theta) * XRoll/inplaneMag /1000
                    fieldY = -Mag * cos(theta) * YRoll/inplaneMag /1000
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
            fieldZ = MagZ /1000
            if inplaneMag >= 0.4:
                # if X >= 0:
                #     fieldX = Mag /1000
                # else:
                #     fieldX = -Mag /1000
                fieldX-0
                fieldY = MagY /1000
            else:
                fieldX = 0
                fieldY = 0

            self.field.B_Global_Desired[0] = fieldX
            self.field.B_Global_Desired[1] = fieldY
            self.field.B_Global_Desired[2] = fieldZ
            self.field.setXYZ(self.field.B_Global_Desired)
            if self.stopped:
                return

    def wrist_gripper(self):
        startTime = time.time()
        while True:
            t = time.time() - startTime
            if self.params[0] == 0: # horizontal plane
                if sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2) >= 0.2:
                    if self.joystick.get_axis(1)<=0:
                        maxField = 10 # absolute value of maximum field
                        By = self.joystick.get_axis(0)*maxField/1000 # field Y, Left X-axis
                        Bx = self.joystick.get_axis(1)*maxField/1000 # field X, Left Y-axis
                        Bz = 0
                    else:
                        if self.joystick.get_axis(0)>0:
                            Bx = 0
                            By = sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*maxField/1000
                            Bz = 0
                        else:
                            Bx = 0
                            By = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*maxField/1000
                            Bz = 0
                    if abs(self.joystick.get_axis(3)) >= 0.2:
                        Bz = self.joystick.get_axis(3)*maxField/1000
                    fieldX = Bx
                    fieldY = By
                    fieldZ = Bz
                elif abs(self.joystick.get_axis(3)) >= 0.2:
                    maxField = 10 # absolute value of maximum field
                    Bz = self.joystick.get_axis(3)*maxField/1000
                    fieldX = 0
                    fieldY = 0
                    fieldZ = Bz
                else:
                    fieldX = 0
                    fieldY = 0
                    fieldZ = 0

            else: # with tilting angle
                if sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2) >= 0.2 and self.joystick.get_axis(1)<=0:
                    maxField = 10
                    theta = atan2(self.joystick.get_axis(0),-self.joystick.get_axis(1))
                    Bx = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*cosd(self.params[0])*cos(theta)*maxField/1000
                    By = sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*sin(theta)*maxField/1000
                    Bz = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*sind(self.params[0])*cos(theta)*maxField/1000
                    if abs(self.joystick.get_axis(3)) >= 0.2:
                        Bx = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*cosd(self.params[0])*cos(theta)*maxField/1000-self.joystick.get_axis(3)*sind(self.params[0])*maxField/1000
                        Bz = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*sind(self.params[0])*cos(theta)*maxField/1000+self.joystick.get_axis(3)*cosd(self.params[0])*maxField/1000
                    fieldX = Bx
                    fieldY = By
                    fieldZ = Bz
                elif sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2) >= 0.2 and self.joystick.get_axis(1)>0: # maintain edge case (>180 deg or <0 deg)
                    maxField = 10
                    if self.joystick.get_axis(0)>0:
                        Bx = 0
                        By = sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*maxField/1000
                        Bz = 0
                        if abs(self.joystick.get_axis(3)) >= 0.2:
                            Bx = -self.joystick.get_axis(3)*sind(self.params[0])*maxField/1000
                            Bz = self.joystick.get_axis(3)*cosd(self.params[0])*maxField/1000
                    else:
                        Bx = 0
                        By = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*maxField/1000
                        Bz = 0
                        if abs(self.joystick.get_axis(3)) >= 0.2:
                            Bx = -self.joystick.get_axis(3)*sind(self.params[0])*maxField/1000
                            Bz = self.joystick.get_axis(3)*cosd(self.params[0])*maxField/1000
                    fieldX = Bx
                    fieldY = By
                    fieldZ = Bz
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

    def wrist_gripper_vertical(self):
        startTime = time.time()
        while True:
            t = time.time() - startTime
            if self.params[0] == 0: # 0 deg vertical plane
                if sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2) >= 0.2:
                    if self.joystick.get_axis(1)<=0: # general control
                        maxField = 10 # absolute value of maximum field
                        Bz = -self.joystick.get_axis(0)*maxField/1000 # field Z, Left X-axis
                        By = 0
                        Bx = self.joystick.get_axis(1)*maxField/1000 # field X, Left Y-axis
                    else: # maintain edge case (>180 deg or <0 deg)
                        maxField = 10 # absolute value of maximum field
                        if self.joystick.get_axis(0)>0:
                            Bz = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*maxField/1000
                            By = 0
                            Bx = 0
                        else:
                            Bz = sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*maxField/1000
                            By = 0
                            Bx = 0
                    if abs(self.joystick.get_axis(3)) >= 0.2:
                        By = self.joystick.get_axis(3)*maxField/1000
                    fieldX = Bx
                    fieldY = By
                    fieldZ = Bz
                elif abs(self.joystick.get_axis(3)) >= 0.2:
                    maxField = 10 # absolute value of maximum field
                    By = self.joystick.get_axis(3)*maxField/1000
                    fieldX = 0
                    fieldY = By
                    fieldZ = 0
                else:
                    fieldX = 0
                    fieldY = 0
                    fieldZ = 0

            else: # with azimuthal angle, under testing
                if sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2) >= 0.2 and self.joystick.get_axis(1)<=0:
                    maxField = 10
                    theta = atan2(self.joystick.get_axis(0),-self.joystick.get_axis(1))
                    Bx = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*cosd(self.params[0])*cos(theta)*maxField/1000
                    By = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*sind(self.params[0])*cos(theta)*maxField/1000
                    Bz = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*sin(theta)*maxField/1000
                    if abs(self.joystick.get_axis(3)) >= 0.2:
                        Bx = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*cosd(self.params[0])*cos(theta)*maxField/1000-self.joystick.get_axis(3)*sind(self.params[0])*maxField/1000
                        By = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*sind(self.params[0])*cos(theta)*maxField/1000+self.joystick.get_axis(3)*cosd(self.params[0])*maxField/1000
                    fieldX = Bx
                    fieldY = By
                    fieldZ = Bz
                elif sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2) >= 0.2 and self.joystick.get_axis(1)>0: # maintain edge case (>180 deg or <0 deg)
                    maxField = 10
                    if self.joystick.get_axis(0)>0:
                        Bx = 0
                        By = 0
                        Bz = -sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*maxField/1000
                        if abs(self.joystick.get_axis(3)) >= 0.2:
                            Bx = -self.joystick.get_axis(3)*sind(self.params[0])*maxField/1000
                            By = self.joystick.get_axis(3)*cosd(self.params[0])*maxField/1000
                    else:
                        Bx = 0
                        By = 0
                        Bz = sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2)*maxField/1000
                        if abs(self.joystick.get_axis(3)) >= 0.2:
                            Bx = -self.joystick.get_axis(3)*sind(self.params[0])*maxField/1000
                            By = self.joystick.get_axis(3)*cosd(self.params[0])*maxField/1000
                    fieldX = Bx
                    fieldY = By
                    fieldZ = Bz
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

    # def cutting_old(self):
    #     startTime = time.time()
    #     while True:
    #         t = time.time() - startTime
    #         if sqrt(self.joystick.get_axis(0)**2+self.joystick.get_axis(1)**2) >= 0.2 and self.joystick.get_axis(1)<0:
    #             phi = atan2(self.joystick.get_axis(0),-self.joystick.get_axis(1))
    #         else:
    #             phi = 0
    #         if abs(self.joystick.get_axis(3)) >= 0.2:
    #             freq = 1*self.joystick.get_axis(3)
    #         else:
    #             freq = 0
    #         mag = 20
    #         theta = 2 * pi * freq * t
    #         if freq == 0:
    #             fieldX = 0
    #             fieldY = 0
    #             fieldZ = 0
    #         else:
    #             fieldX = -mag * sin(phi) * cos(theta)
    #             fieldY = mag * sin(theta)
    #             fieldZ = mag * cos(phi) * cos(theta)
    #
    #         self.field.B_Global_Desired[0] = fieldX/1000
    #         self.field.B_Global_Desired[1] = fieldY/1000
    #         self.field.B_Global_Desired[2] = fieldZ/1000
    #         self.field.setXYZ(self.field.B_Global_Desired)
    #
    #         if self.stopped:
    #             return

    def cutting(self):
        startTime = time.time()
        while True:
            t = time.time() - startTime
            freq = 1

            # q components
            q_1 = radians(30) # angle to be modified
            q_2 = radians(30) # angle to be modified
            q_3 = radians(2 * pi * freq * t)

            # n_3 components
            n_3x = -cos(q_1) * sin(q_3) - cos(q_3) * sin(q_1) * sin(q_2)
            n_3y = -sin(q_1) * sin(q_3) + cos(q_1) * cos(q_3) * sin(q_2)
            n_3z = -cos(q_2) * cos(q_3)

            # a_3 components
            a_3x = -cos(q_2) * sin(q_1)
            a_3y = cos(q_1) * cos(q_2)
            a_3z = sin(q_2)

            # n_2 components
            n_2x = -sin(q_1) * sin(q_2)
            n_2y = cos(q_1) * sin(q_2)
            n_2z = -cos(q_2)

            # a_2 components
            a_2x = cos(q_1)
            a_2y = sin(q_1)
            a_2z = 0

            # a_1 components
            a_1x = 0
            a_1y = 0
            a_1z = 1

            # h components
            h_1 = n_3z * a_3y - n_3y * a_3z
            h_2 = n_3x * a_3z - n_3z * a_3x
            h_3 = n_3y * a_3x - n_3x * a_3y

            # s components
            s_1 = n_3z * a_2y - n_3y * a_2z
            s_2 = n_3x * a_2z - n_3z * a_2x
            s_3 = n_3y * a_2x - n_3x * a_2y

            # f components
            f_1 = -n_3y * a_1z
            f_2 = n_3x * a_1z
            f_3 = 0

            J_3 = 1 # moment of inertia to be modified
            q_3ddot = 0
            tau_f3 = 0 # friction torque to be modified
            tau_tissue = 1 # tissue torque to be modified
            X_1 = J_3 * q_3ddot + tau_f3 + tau_tissue

            m_3 = 0.001 # mass to be modified, unit kg
            g = 9.8
            l_2 = 0.005 # link length to be modified, unit meter
            J_2 = 1 # moment of inertia to be modified
            q_2ddot = 0
            tau_f2 = 0 # friction torque to be modified
            X_2 = -m_3 * g * l_2 * sin(q_2) + J_2 * q_2ddot + tau_f2

            J_1 = 1 # moment of inertia to be modified
            q_1ddot = 0
            tau_f1 = 0 # friction torque to be modified
            X_3 = J_1 * q_1ddot + tau_f1

            m = 1 # magnetic moment of magnet

            fieldX = -(f_3 * s_2 * X_1 - f_2 * s_3 * X_1 + f_2 * h_3 * X_2 - f_3 * h_2 * X_2 + h_2 * s_3 * X_3 - h_3 * s_2 * X_3) / (m * (f_3 * h_2 * s_1 - f_2 * h_3 * s_1 - f_3 * h_1 * s_2 + f_1 * h_3 * s_2 + f_2 * h_1 * s_3 - f_1 * h_2 * s_3))
            fieldY = -(f_1 * s_3 * X_1 - f_3 * s_1 * X_1 + f_3 * h_1 * X_2 - f_1 * h_3 * X_2 + h_3 * s_1 * X_3 - h_1 * s_3 * X_3) / (m * (f_3 * h_2 * s_1 - f_2 * h_3 * s_1 - f_3 * h_1 * s_2 + f_1 * h_3 * s_2 + f_2 * h_1 * s_3 - f_1 * h_2 * s_3))
            fieldZ = -(f_2 * s_1 * X_1 - f_1 * s_2 * X_1 + f_1 * h_2 * X_2 - f_2 * h_1 * X_2 + h_1 * s_2 * X_3 - h_2 * s_1 * X_3) / (m * (f_3 * h_2 * s_1 - f_2 * h_3 * s_1 - f_3 * h_1 * s_2 + f_1 * h_3 * s_2 + f_2 * h_1 * s_3 - f_1 * h_2 * s_3))

            self.field.B_Global_Desired[0] = fieldX/1000
            self.field.B_Global_Desired[1] = fieldY/1000
            self.field.B_Global_Desired[2] = fieldZ/1000
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
