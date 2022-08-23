# assign pin # to the coil
# PIN_X1 = [0, 5.003] # pin number, factor number (mT/V)
# PIN_X2 = [3, 4.879]
# PIN_Y1 = [4, 5.143]
# PIN_Y2 = [1, 5.024]
# PIN_Z1 = [2, 5.024]
# PIN_Z2 = [5, 4.433]

PIN_X1 = [5, 5.602] # pin number, factor number (mT/V)
PIN_X2 = [1, 4.850]
PIN_Y1 = [2, 4.486]
PIN_Y2 = [6, 6.200]
PIN_Z1 = [3, 5.366]
PIN_Z2 = [7, 4.508]

# PIN_X1 = [5, 2.801] # pin number, factor number (mT/V)
# PIN_X2 = [1, 2.425]
# PIN_Y1 = [2, 2.243]
# PIN_Y2 = [6, 3.100]
# PIN_Z1 = [3, 2.683]
# PIN_Z2 = [7, 2.254]

class FieldManager(object):
    def __init__(self,dac):
        self.x = 0
        self.y = 0
        self.z = 0
        self.freq = 0
        self.mag = 0
        self.dac = dac

    # Uniform field
    def setX(self,mT):
        self.dac.s826_aoPin(PIN_X1[0], mT / PIN_X1[1])
        self.dac.s826_aoPin(PIN_X2[0], mT / PIN_X2[1])
        self.x = mT

    def setY(self,mT):
        self.dac.s826_aoPin(PIN_Y1[0], mT / PIN_Y1[1])
        self.dac.s826_aoPin(PIN_Y2[0], mT / PIN_Y2[1])
        self.y = mT

    def setZ(self,mT):
        self.dac.s826_aoPin(PIN_Z1[0], mT / PIN_Z1[1])
        self.dac.s826_aoPin(PIN_Z2[0], mT / PIN_Z2[1])
        self.z = mT

    def setXYZ(self,x_mT,y_mT,z_mT):
        self.setX(x_mT)
        self.setY(y_mT)
        self.setZ(z_mT)


    # def setXGradient(self,uniformX,gradientX):
    #     if gradientX > 0:
    #         self.dac.s826_aoPin(PIN_X1[0], gradientX / PIN_X1[1])
    #         self.dac.s826_aoPin(PIN_X2[0], 0 / PIN_X2[1])
    #     else:
    #         self.dac.s826_aoPin(PIN_X1[0], 0 / PIN_X1[1])
    #         self.dac.s826_aoPin(PIN_X2[0], gradientX / PIN_X2[1])

    # Generate a pulling force by applying current to only one coil
    # mT is a measurement of current in the coil. It has nothing to do with actual field strength.
    def setXGradient(self,uniformX,gradientX):
        if gradientX >= 0:
            self.dac.s826_aoPin(PIN_X1[0], (uniformX+gradientX) / PIN_X1[1])
            self.dac.s826_aoPin(PIN_X2[0], (0) / PIN_X2[1])
            print(uniformX+gradientX)
        else:
            self.dac.s826_aoPin(PIN_X1[0], (0) / PIN_X1[1])
            self.dac.s826_aoPin(PIN_X2[0], (-uniformX-gradientX) / PIN_X2[1])
            print(uniformX+gradientX)
        self.x = uniformX

    def setYGradient(self,uniformY,gradientY):
        if uniformY >= 0:
            self.dac.s826_aoPin(PIN_Y1[0], (uniformY+gradientY) / PIN_Y1[1])
            self.dac.s826_aoPin(PIN_Y2[0], (uniformY-gradientY) / PIN_Y2[1])
        else:
            self.dac.s826_aoPin(PIN_Y1[0], (uniformY-gradientY) / PIN_Y1[1])
            self.dac.s826_aoPin(PIN_Y2[0], (uniformY+gradientY) / PIN_Y2[1])
        self.y = uniformY

    def setZGradient(self,uniformZ,gradientZ):
        if uniformZ >= 0:
            self.dac.s826_aoPin(PIN_Z1[0], (uniformZ+gradientZ) / PIN_Z1[1])
            self.dac.s826_aoPin(PIN_Z2[0], (uniformZ-gradientZ) / PIN_Z2[1])
        else:
            self.dac.s826_aoPin(PIN_Z1[0], (uniformZ-gradientZ) / PIN_Z1[1])
            self.dac.s826_aoPin(PIN_Z2[0], (uniformZ+gradientZ) / PIN_Z2[1])
        self.z = uniformZ

    def setFrequency(self,Hz):
        self.freq = Hz

    def setMagnitude(self,mT):
        self.mag = mT
