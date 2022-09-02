# assign pin # to the coil
PIN_X1 = [5, 5.602] # pin number, factor number (mT/V)
PIN_X2 = [1, 4.850]
PIN_Y1 = [2, 4.486]
PIN_Y2 = [6, 6.200]
PIN_Z1 = [3, 5.366]
PIN_Z2 = [7, 4.508]

numField = 3
numGrad = 5
numAct = 8
# Declare the control matrix for relating the currents to the magnetic field and gradients
# This matrix considers the gradients as well as the field components
N_list = [[0.0036336,	-0.00078,	-0.004188,	-0.0172944,	 0.01758,	-0.0034944,	 0.0017976,	 0.0040032 ],
       [  0.0037728,	 0.0181776,	 0.003588,	-0.0010728,	 0.0008232,	-0.0040848,	-0.0170712,	-0.0036168 ],
       [ -0.0007968,	 0.0125472,	-0.0012336,	 0.012252,	 0.01212,	-0.0011952,	 0.0121992,	-0.0011472 ],
       [ -0.0153312,	 0.15354,	-0.0191832,	-0.0795432,	-0.0935904,	-0.012216,	 0.1548408,	-0.0230928 ],
       [ -0.0383184,	 0.0036216,	 0.0412104,	-0.0063,	-0.0008544,	-0.0371352,	 0.015732,	 0.0364968 ],
       [ -0.0083544,	 0.0153336,	 0.0099864,	 0.2313216,	-0.2274,	 0.0070104,	-0.011592,	-0.01098   ],
       [ -0.0187776,	-0.0901176,	-0.0144816,	 0.1492368,	 0.1640112,	-0.0203568,	-0.0964416,	-0.0139104 ],
       [ -0.0108264,	-0.247728,	-0.0094248,	 0.0090024,	-0.0205296,	 0.0097824,	 0.2304216,	 0.0087936 ]]
# Declare the control matrix for relating the currents to the magnetic field
# This matrix does not consider the gradients, only the field components
M_list = [[0.0036336,	-0.00078,	-0.004188,	-0.0172944,	 0.01758,	-0.0034944,	 0.0017976,	 0.0040032 ],
       [  0.0037728,	 0.0181776,	 0.003588,	-0.0010728,	 0.0008232,	-0.0040848,	-0.0170712,	-0.0036168 ],
       [ -0.0007968,	 0.0125472,	-0.0012336,	 0.012252,	 0.01212,	-0.0011952,	 0.0121992,	-0.0011472 ]]


class FieldManager(object):
    def __init__(self,dac):
        self.x = 0
        self.y = 0
        self.z = 0
        self.freq = 0
        self.mag = 0
        self.dac = dac
        self.N = np.array(N_list) # N matrix
        self.M = np.array(M_list) # M matrix
        self.invN = np.linalg.inv(N) # inverse of N matrix
        self.overheatFlag = False
        self.isGradControlled = False

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

    def setXYZ(self,B_Global_Desired):
        self.x = B_Global_Desired[0]
        self.y = B_Global_Desired[1]
        self.z = B_Global_Desired[2]
        self.updateCurrent(B_Global_Desired)


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

    def setOverheatFlag(self,state):
        self.overheatFlag = state

    def setGradientFlag(self,state):
        self.isGradControlled = state

    def updateCurrent(self,B_Global_Desired):
        if not self.overheatFlag:
            if self.isGradControlled:
                for i in range(numAct):
                    sum = 0
                    for j in range(numField+numGrad):
                        sum += invN[i][j]*B_Global_Desired[j]
