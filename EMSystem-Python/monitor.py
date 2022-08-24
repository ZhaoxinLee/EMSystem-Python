PIN_NEG_T0 = 21 # pin number
PIN_POS_T0 = 22
PIN_NEG_T1 = 23
PIN_POS_T1 = 24
PIN_NEG_T2 = 25
PIN_POS_T2 = 26
PIN_NEG_T3 = 27
PIN_POS_T3 = 28
PIN_NEG_T4 = 29
PIN_POS_T4 = 30
PIN_NEG_T5 = 31
PIN_POS_T5 = 32
PIN_NEG_T6 = 33
PIN_POS_T6 = 34
PIN_NEG_T7 = 35
PIN_POS_T7 = 36

class Monitor(object):
    def __init__(self,adc):
        self.adc = adc
        self.aiVoltage = [0]*16 # 16 input channels of analog voltage
        self.measuredData = [0]*16

    def setMonitor(self):
        aiVoltage = self.adc.s826_aiPin(self.aiVoltage)
        self.aiVoltage = aiVoltage
        currentSenseAdj = [6.7501, 6.6705, 6.4118, 3.8831, 6.7703, 6.7703, 6.7107, 6.8500]
        tempSenseAdj = [20]*8
        for i in range(8):
            self.measuredData[i] = self.aiVoltage[i]*currentSenseAdj[i] # measured current
            self.measuredData[i+8] = self.aiVoltage[i+8]*tempSenseAdj[i] # measured temp
        return self.measuredData
