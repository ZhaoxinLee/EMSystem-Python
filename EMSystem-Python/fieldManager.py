import numpy as np

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
maxCurrent = 24
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

currentControlAdj = [1.0/6.7501, 1.0/6.6705, 1.0/6.4118, 1.0/6.7818, 1.0/6.7703, 1.0/6.7703, 1.0/6.7107, 1.0/6.8500]


class FieldManager(object):
    def __init__(self,dac):
        self.x = 14
        self.freq = 0
        self.mag = 0
        self.dac = dac
        self.N = np.array(N_list) # N matrix
        self.M = np.array(M_list) # M matrix
        # inverse of N matrix, pinv returns the inverse of your matrix when it is available and the pseudo inverse when the matrix is singular or nonsquare
        self.invN = np.linalg.pinv(self.N)
        self.invM = np.linalg.pinv(self.M)
        self.B_Global_Desired = [0]*8
        self.currentSetpoints = [0]*8
        self.outputAnalogVoltages = [0]*8
        self.overheatFlag = False
        self.isGradControlled = False

    # Uniform field
    # def setX(self,mT):
    #     self.dac.s826_aoPin(PIN_X1[0], mT / PIN_X1[1])
    #     self.dac.s826_aoPin(PIN_X2[0], mT / PIN_X2[1])
    #     self.x = mT
    #
    # def setY(self,mT):
    #     self.dac.s826_aoPin(PIN_Y1[0], mT / PIN_Y1[1])
    #     self.dac.s826_aoPin(PIN_Y2[0], mT / PIN_Y2[1])
    #     self.y = mT
    #
    # def setZ(self,mT):
    #     self.dac.s826_aoPin(PIN_Z1[0], mT / PIN_Z1[1])
    #     self.dac.s826_aoPin(PIN_Z2[0], mT / PIN_Z2[1])
    #     self.z = mT

    def setXYZ(self,B_Global_Desired):
        for i in range(numField):
            self.B_Global_Desired[i] = B_Global_Desired[i]
        self.updateCurrent()

    def setGradient(self,B_Global_Desired):
        for i in range(numField,numField+numGrad):
            self.B_Global_Desired[i] = B_Global_Desired[i]
        self.updateCurrent()

    def setFrequency(self,Hz):
        self.freq = Hz

    def setMagnitude(self,mT):
        self.mag = mT

    def updateCurrent(self):
        if not self.overheatFlag:
            if self.isGradControlled:
                maxCurrentBuf = 0
                for i in range(numAct):
                    sum = 0
                    for j in range(numField+numGrad):
                        sum += self.invN[i][j]*self.B_Global_Desired[j]
                    self.currentSetpoints[i] = sum
                    if abs(self.currentSetpoints[i]) > maxCurrentBuf:
                        maxCurrentBuf = abs(self.currentSetpoints[i])
                if maxCurrentBuf > 1:
                    scalingFactor = 1/maxCurrentBuf # Check that none of the currents are above the max by finding the max and scaling all down accordingly afterwards.
                    for i in range(numAct):
                        self.currentSetpoints[i] *= scalingFactor
                        self.currentSetpoints[i] *= maxCurrent
                else:
                    for i in range(numAct):
                        self.currentSetpoints[i] *= maxCurrent
                print("Current setpoints with gradients:", self.currentSetpoints)
            else:
                maxCurrentBuf = 0
                for i in range(numAct):
                    sum = 0
                    for j in range(numField):
                        sum += self.invM[i][j]*self.B_Global_Desired[j]
                    self.currentSetpoints[i] = sum
                    if abs(self.currentSetpoints[i]) > maxCurrentBuf:
                        maxCurrentBuf = abs(self.currentSetpoints[i])
                if maxCurrentBuf > 1:
                    scalingFactor = 1/maxCurrentBuf # Check that none of the currents are above the max by finding the max and scaling all down accordingly afterwards.
                    print('scaling factor:',scalingFactor)
                    for i in range(numAct):
                        self.currentSetpoints[i] *= scalingFactor
                        self.currentSetpoints[i] *= maxCurrent
                else:
                    for i in range(numAct):
                        self.currentSetpoints[i] *= maxCurrent
                print("Current setpoints without gradients:", self.currentSetpoints)
            for i in range(numAct):
                self.outputAnalogVoltages[i] = self.currentSetpoints[i] * currentControlAdj[i]
        else:
            for i in range(numAct):
                self.outputAnalogVoltages[i] = 0
            print("Currents cleared!")

        self.dac.s826_aoWriteAll(self.outputAnalogVoltages)
