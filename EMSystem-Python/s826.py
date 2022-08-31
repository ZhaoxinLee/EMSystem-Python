from ctypes import *
import numpy as np
s826dll = cdll.LoadLibrary("./s826.dll") # for Windows system
# s826dll = cdll.LoadLibrary("./lib826_64.so") # for Linux system
BOARD = 1 # The board identifier is assumed to be always 0 (All switches OFF).
TSETTLE = 250 # can be set as low as 0. Lower is faster, but higher is less noise.
TMAX = 500 # ADC. Max time allowed to read analog signals

# As we cannot export macros from c++ dll file, here we manually define the macros we are going to use only
# For other macros that will be used for further s826 functions, please refer to s826api.h to see the definition
COUNTER_CHAN = 5 # Counter channel number
# TMR_MODE  (S826_CM_K_1MHZ | S826_CM_UD_REVERSE | S826_CM_PX_ZERO | S826_CM_PX_START | S826_CM_OM_NOTZERO)
S826_CM_K_1MHZ = 2 << 4
S826_CM_UD_REVERSE = 1 << 22
S826_CM_PX_ZERO = 1 << 13
S826_CM_PX_START = 1 << 24
S826_CM_OM_NOTZERO = 3 << 18
TMR_MODE = S826_CM_K_1MHZ | S826_CM_UD_REVERSE | S826_CM_PX_ZERO | S826_CM_PX_START | S826_CM_OM_NOTZERO
CLEAR_BITS = 0x0000000

RANGE_PARAM = [[0,5],[0,10],[-5,10],[-10,20]] # DAC rangeCode = 0, 1, 2, 3     [lowerV,rangeV]
RANGE_PARAM_2 = [[-10,20],[-5,10],[-2,4],[-1,2]] # ADC rangeCode = 0, 1, 2, 3     [lowerV,rangeV]



class S826(object):
    def __init__(self):
        self.lowerV = [-5,-5,-5,-5,-5,-5,-5,-5]  # default range selection = 2
        self.rangeV = [10,10,10,10,10,10,10,10]  # default range selection = 2
        self.lowerV_2 = [-10,-10,-10,-10,-10,-10,-10,-10,-10,-10,-10,-10,-10,-10,-10,-10]  # default range selection = 0
        self.rangeV_2 = [20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20]  # default range selection = 0
        self.boardConnected = False
        self.aiV = [0]*16
        boardflags  = self.s826_init() # Here 0 means no board and 1 mean board 0 found, for only 1 board connected the function should return 2^(ID#)
        if boardflags != 2:
            print('Cannot detect s826 board. Error code: {}'.format(boardflags))
            self.s826_close()
        else:
            self.boardConnected = True
            print("S826_SystemOpen() returned the value: {}".format(boardflags))
            print("The board number is: {}".format(int(np.log2(boardflags))))
        if self.boardConnected:
            self.X826(s826dll.S826_CounterStateWrite(BOARD, COUNTER_CHAN, 0))     # halt channel if it's running
            self.X826(s826dll.S826_CounterModeWrite(BOARD, COUNTER_CHAN, TMR_MODE))     # configure counter as periodic timer
            #print(bin(TMR_MODE))
            self.s826_initDac()
            self.s826_initAdc()

    def s826_init(self):
        errCode = s826dll.S826_SystemOpen()
        return errCode

    def s826_close(self):
        if self.boardConnected:
            self.X826(s826dll.S826_CounterModeWrite(BOARD, COUNTER_CHAN, CLEAR_BITS))
            self.X826(s826dll.S826_AdcEnableWrite(BOARD, 0))
        s826dll.S826_SystemClose()

    def s826_initDac(self):
        for i in range(8):
            self.s826_setDacRange(i,2) # default range selection = 2

    def s826_initAdc(self):
        for i in range(16):
            # self.s826_setAdcRange(i,0) # default range selection = 0
            self.X826(s826dll.S826_AdcSlotConfigWrite(BOARD,i,i,TSETTLE,0))
        self.X826(s826dll.S826_AdcSlotlistWrite(BOARD, 0xFFFF, 0)) # enable all ADC timeslots
        # slotlist = pointer(c_uint())
        # self.X826(s826dll.S826_AdcSlotlistRead(BOARD, slotlist))
        # print(bin(slotlist[0]))
        self.X826(s826dll.S826_AdcTrigModeWrite(BOARD, 0)) # disable ADC hardware triggering, use continuous mode
        self.X826(s826dll.S826_AdcEnableWrite(BOARD, 1)) # enable ADC conversions

    # ======================================================================
    # rangeCode: 0: 0 +5V; 1: 0 +10V; 2: -5 +5V; 3:-10 +10V.
    # ======================================================================
    def s826_setDacRange(self,chan,rangeCode):
        self.lowerV[chan] = RANGE_PARAM[rangeCode][0]
        self.rangeV[chan] = RANGE_PARAM[rangeCode][1]
        self.X826(s826dll.S826_DacRangeWrite(BOARD,chan,rangeCode,0)) # BOARD, chan, rangeCode, output V

    # ======================================================================
    # rangeCode: 0: -10 +10V; 1: -5 +5V; 2: -2 +2V; 3:-1 +1V.
    # ======================================================================
    def s826_setAdcRange(self,chan,rangeCode):
        self.lowerV_2[chan] = RANGE_PARAM_2[rangeCode][0]
        self.rangeV_2[chan] = RANGE_PARAM_2[rangeCode][1]
        self.X826(s826dll.S826_AdcSlotConfigWrite(BOARD,chan,chan,TSETTLE,rangeCode)) # BOARD, timeslot, chan, tsettle, range


    # ======================================================================
    # Set 1 AO channel.
    # chan : DAC channel # in the range 0 to 7.
    # outputV: Desired analog output voltage (can be positive and negative).
    # ======================================================================
    def s826_aoPin(self,chan,outputV):
        lowerV = self.lowerV[chan]
        rangeV = self.rangeV[chan]
        setpoint = int((outputV-lowerV)/rangeV*0xffff)
        self.X826(s826dll.S826_DacDataWrite(BOARD,chan,setpoint,0))

# ======================================================================
# Set 16 AI channel.
# chan : ADC channel # in the range 0 to 15.
# chan 8-15: thermometer reading.
# ======================================================================
    def s826_aiReadAll(self,aiV):
        tstamp = None
        # slotlist = bytes(c_uint(0xFFFF))
        slotlist = pointer(c_uint(0xFF0F))
        adcbuf = pointer(c_int())
        # for i in range(1):

        #     adcbuf[i] = c_int(1)
            # print('buf',adcbuf[i])
            # slotlist[i] = c_uint(1)
        # print('slot',bin(slotlist[0]))
        errcode = s826dll.S826_AdcRead(BOARD, adcbuf, tstamp, slotlist, TMAX)
        # if errcode == 0:
        #     print("Analog input read successfully...")
        # else:
        #     print("Error in reading analog input: {}".format(errcode))

        # Read adc value for each channel
        resolution = 20.0 / 65536.0 # default range -10V to 10V
        for i in range(16):
            singleReading = adcbuf[i] & 0xFFFF
            if singleReading & 0x8000:
                aiV[i] = ( ( ~(singleReading-1) ) & 0xFFFF ) * resolution # subtract 1 due to range of integers being −32,768 to 32,767
                aiV[i] = -1.0 * aiV[i]
            else:
                aiV[i] = singleReading * resolution
        # currentSenseAdj = [6.7501, 6.6705, 6.4118, 3.8831, 6.7703, 6.7703, 6.7107, 6.8500]
        # for i in range(8):
        #     print("Analog input voltage 0-7:",bin(adcbuf[i]),aiV[i]*currentSenseAdj[i])
        # for i in range(8,16):
        #     print("Analog input voltage 8-15:",bin(adcbuf[i]),20*aiV[i])
        return aiV

# ERROR HANDLING
# These examples employ very simple error handling: if an error is detected, the example functions will immediately return an error code.
# This behavior may not be suitable for some real-world applications but it makes the code easier to read and understand. In a real
# application, it's likely that additional actions would need to be performed. The examples use the following X826 macro to handle API
# function errors; it calls an API function and stores the returned value in errcode, then returns immediately if an error was detected.
    def X826(self,func):
        errcode = func
        if errcode != 0:
            print("Error: {}".format(errcode))
