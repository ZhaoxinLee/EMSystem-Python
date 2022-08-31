
class Monitor(object):
    def __init__(self,adc):
        self.adc = adc
        self.aiVoltage = [0]*16 # 16 input channels of analog voltage
        self.measuredData = [0]*16
        self.monitorFlag = True

    def setMonitor(self):
        aiVoltage = self.adc.s826_aiReadAll(self.aiVoltage)
        self.aiVoltage = aiVoltage
        currentSenseAdj = [6.7501, 6.6705, 6.4118, 3.8831, 6.7703, 6.7703, 6.7107, 6.8500]
        tempSenseAdj = [20]*8
        for i in range(8):
            self.measuredData[i] = round(self.aiVoltage[i]*currentSenseAdj[i],2) # measured current
            self.measuredData[i+8] = round(self.aiVoltage[i+8]*tempSenseAdj[i],2) # measured temp
        return self.measuredData
