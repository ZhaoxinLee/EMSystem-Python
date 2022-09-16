from PyQt5 import uic
from PyQt5.QtCore import QFile, QRegExp, QTimer, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMenu, QMessageBox
from s826 import S826
from monitor import Monitor
from fieldManager import FieldManager
from vision import Vision
# from vision2 import Vision2
from subThread import SubThread
from realTimePlot import CustomFigCanvas
from XboxController import Xbox
import time
import numpy as np

#=========================================================
# UI Config
#=========================================================
qtCreatorFile = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

s826 = S826()
monitor = Monitor(s826)
field = FieldManager(s826)
vision = Vision(field,'Video') # greyscale mode
# vision2 = Vision2(field,index=2,type='firewire') # greyscale mode
# joystick = Xbox()

#=========================================================
# a class that handles the signal and callbacks of the GUI
#=========================================================
class GUI(QMainWindow,Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self,None,Qt.WindowStaysOnTopHint)
        Ui_MainWindow.__init__(self)
        self.updateRate = 15 # (ms) update rate of the GUI, vision, plot
        self.measuredData = [0]*16
        self.aiVoltage = [0]*16
        self.B_Global_Desired = [0]*8
        self.setupUi(self)
        self.setupTimer()
        try:
            joystick
        except NameError:
            self.setupSubThread(field,vision)#,vision2)
        else:
            self.setupSubThread(field,vision,joystick)
        self.connectSignals()
        self.linkWidgets()
        self.setupRealTimePlot() # comment on this line if you don't want a preview window

    #=====================================================
    # [override] terminate the subThread and clear currents when closing the window
    #=====================================================
    def closeEvent(self,event):
        #self.thrd.stop()
        # self.timer.stop()
        # vision.closeCamera()
        # try:
        #     vision2
        # except NameError:
        #     pass
        # else:
        #     vision2.closeCamera()
        # try:
        #     joystick
        # except NameError:
        #     pass
        # else:
        #     joystick.quit()
        # self.clearField()
        s826.s826_close()
        event.accept()


    #=====================================================
    # QTimer handles updates of the GUI, run at 60Hz
    #=====================================================
    def setupTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.updateRate) # msec

        self.monitorTimer = QTimer()
        self.monitorTimer.timeout.connect(self.updateMonitor)
        self.monitorTimer.start(100)

        self.captionTimer = QTimer()
        self.captionTimer.timeout.connect(self.updateCaption)
        self.captionTimer.start(100)

    def update(self):
        vision.updateFrame()
        # try:
        #     vision2
        # except NameError:
        #     pass
        # else:
        #     vision2.updateFrame()
        try:
            self.realTimePlot
        except AttributeError:
            pass
        else:
            self.updatePlot()
        # try:
        #     joystick
        # except NameError:
        #     pass
        # else:
        #     joystick.update()


    def updateMonitor(self):
        self.measuredData = monitor.setMonitor()

        # check that the temperature in any core is not above the max value
#!!!!!!!!!!!!!!!!! NEVER change or comment below code!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!! This is the only place to moniter overheating of the system!!!!!!!!!!!
        # if any(self.measuredData[i+8] > 90 for i in range(8)):
        #     print("Overheating! Currents clearing...")
        #     field.overheatFlag = True
        #     field.updateCurrent()
        #     msgBox = QMessageBox()
        #     msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)
        #     msgBox.setIcon(QMessageBox.Information)
        #     msgBox.setText("<p>Overheating! Currents clearing...</p>")
        #     msgBox.setWindowTitle("Warning!")
        #     msgBox.setStandardButtons(QMessageBox.Ok)
        #     msgBox.exec()
        #     self.monitorTimer.stop()

    #=====================================================
    # Connect buttons etc. of the GUI to callback functions
    #=====================================================
    def connectSignals(self):
        # General Control Tab
        self.dsb_x.valueChanged.connect(self.setFieldXYZ)
        self.dsb_y.valueChanged.connect(self.setFieldXYZ)
        self.dsb_z.valueChanged.connect(self.setFieldXYZ)
        self.btn_clearCurrent.clicked.connect(self.clearField)
        self.dsb_xxGradient.valueChanged.connect(self.setFieldGradient)
        self.dsb_xyGradient.valueChanged.connect(self.setFieldGradient)
        self.dsb_xzGradient.valueChanged.connect(self.setFieldGradient)
        self.dsb_yyGradient.valueChanged.connect(self.setFieldGradient)
        self.dsb_yzGradient.valueChanged.connect(self.setFieldGradient)

        # Subthread Tab
        # self.cbb_subThread.currentTextChanged.connect(self.on_cbb_subThread)
        # self.cbb_subThread.currentTextChanged.connect(self.on_chb_changeSubthread)
        # self.cbb_subThread.currentTextChanged.connect(self.on_chb_switchSubthread)
        # self.chb_startStopSubthread.toggled.connect(self.on_chb_startStopSubthread)
        # self.dsb_subThreadParam0.valueChanged.connect(self.thrd.setParam0)
        # self.dsb_subThreadParam1.valueChanged.connect(self.thrd.setParam1)
        # self.dsb_subThreadParam2.valueChanged.connect(self.thrd.setParam2)
        # self.dsb_subThreadParam3.valueChanged.connect(self.thrd.setParam3)
        # self.dsb_subThreadParam4.valueChanged.connect(self.thrd.setParam4)


    #=====================================================
    # Link GUI elements
    #=====================================================
    def linkWidgets(self):
        # link slider to doubleSpinBox
        self.dsb_x.valueChanged.connect(lambda value: self.hsld_x.setValue(int(value*100)))
        self.dsb_y.valueChanged.connect(lambda value: self.hsld_y.setValue(int(value*100)))
        self.dsb_z.valueChanged.connect(lambda value: self.hsld_z.setValue(int(value*100)))
        self.hsld_x.valueChanged.connect(lambda value: self.dsb_x.setValue(float(value/100)))
        self.hsld_y.valueChanged.connect(lambda value: self.dsb_y.setValue(float(value/100)))
        self.hsld_z.valueChanged.connect(lambda value: self.dsb_z.setValue(float(value/100)))

        self.dsb_xxGradient.valueChanged.connect(lambda value: self.hsld_xxGradient.setValue(int(value*100)))
        self.dsb_xyGradient.valueChanged.connect(lambda value: self.hsld_xyGradient.setValue(int(value*100)))
        self.dsb_xzGradient.valueChanged.connect(lambda value: self.hsld_xzGradient.setValue(int(value*100)))
        self.dsb_yyGradient.valueChanged.connect(lambda value: self.hsld_yyGradient.setValue(int(value*100)))
        self.dsb_yzGradient.valueChanged.connect(lambda value: self.hsld_yzGradient.setValue(int(value*100)))
        self.hsld_xxGradient.valueChanged.connect(lambda value: self.dsb_xxGradient.setValue(float(value/100)))
        self.hsld_xyGradient.valueChanged.connect(lambda value: self.dsb_xyGradient.setValue(float(value/100)))
        self.hsld_xzGradient.valueChanged.connect(lambda value: self.dsb_xzGradient.setValue(float(value/100)))
        self.hsld_yyGradient.valueChanged.connect(lambda value: self.dsb_yyGradient.setValue(float(value/100)))
        self.hsld_yzGradient.valueChanged.connect(lambda value: self.dsb_yzGradient.setValue(float(value/100)))

    def updateCaption(self):
        self.lbl_temp_0.setText(str(self.measuredData[8]))
        self.lbl_temp_1.setText(str(self.measuredData[9]))
        self.lbl_temp_2.setText(str(self.measuredData[10]))
        self.lbl_temp_3.setText(str(self.measuredData[11]))
        self.lbl_temp_4.setText(str(self.measuredData[12]))
        self.lbl_temp_5.setText(str(self.measuredData[13]))
        self.lbl_temp_6.setText(str(self.measuredData[14]))
        self.lbl_temp_7.setText(str(self.measuredData[15]))
        self.lbl_V0.setText(str(round(field.outputAnalogVoltages[0],2)))
        self.lbl_V1.setText(str(round(field.outputAnalogVoltages[1],2)))
        self.lbl_V2.setText(str(round(field.outputAnalogVoltages[2],2)))
        self.lbl_V3.setText(str(round(field.outputAnalogVoltages[3],2)))
        self.lbl_V4.setText(str(round(field.outputAnalogVoltages[4],2)))
        self.lbl_V5.setText(str(round(field.outputAnalogVoltages[5],2)))
        self.lbl_V6.setText(str(round(field.outputAnalogVoltages[6],2)))
        self.lbl_V7.setText(str(round(field.outputAnalogVoltages[7],2)))

    #=====================================================
    # Thread Example
    #=====================================================
    def setupSubThread(self,field,vision=None,joystick=None):
        if joystick:
            self.thrd = SubThread(field,vision,joystick)
        else:
            self.thrd = SubThread(field,vision)#,vision2)
        self.thrd.statusSignal.connect(self.updateSubThreadStatus)
        self.thrd.finished.connect(self.finishSubThreadProcess)

    # updating GUI according to the status of the subthread
    @pyqtSlot(str)
    def updateSubThreadStatus(self, receivedStr):
        print('Received message from subthread: ',receivedStr)
        # show something on GUI

    # run when the subthread is termianted
    @pyqtSlot()
    def finishSubThreadProcess(self):
        print('Subthread is terminated.')

        vision.clearDrawingRouting()
        self.clearField()
        # disable some buttons etc.

    #=====================================================
    # Real time plot
    # This is showing actual coil current that is stored in field.x, field.y, field.z
    # Note: the figure is updating at the speed of self.updateRate defined in _init_
    #=====================================================
    def setupRealTimePlot(self):
        self.realTimePlot = CustomFigCanvas()
        #self.realTimePlot2 = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.realTimePlot, *(0,0)) # put the preview window in the layout
        self.btn_zoom.clicked.connect(self.realTimePlot.zoom) # connect qt signal to zoom funcion

    def updatePlot(self):
        self.realTimePlot.addDataX(self.dsb_x.value())
        self.realTimePlot.addDataY(self.dsb_y.value())
        self.realTimePlot.addDataZ(self.dsb_z.value())
        self.realTimePlot.addDataA1(field.currentSetpoints[0])
        self.realTimePlot.addDataA2(field.currentSetpoints[1])
        self.realTimePlot.addDataA3(field.currentSetpoints[2])
        self.realTimePlot.addDataA4(field.currentSetpoints[3])
        self.realTimePlot.addDataA5(field.currentSetpoints[4])
        self.realTimePlot.addDataA6(field.currentSetpoints[5])
        self.realTimePlot.addDataA7(field.currentSetpoints[6])
        self.realTimePlot.addDataA8(field.currentSetpoints[7])

    #=====================================================
    # Callback Functions
    #=====================================================
    # General control tab
    def setFieldXYZ(self):
        self.B_Global_Desired[0] = self.dsb_x.value()/1000 # mT -> T
        self.B_Global_Desired[1] = self.dsb_y.value()/1000 # mT -> T
        self.B_Global_Desired[2] = self.dsb_z.value()/1000 # mT -> T
        field.setXYZ(self.B_Global_Desired)
        # field.setMagnitude(round(sqrt(pow(self.dsb_x.value(),2)+pow(self.dsb_y.value(),2)+pow(self.dsb_z.value(),2)),2))

    def setFieldGradient(self):
        self.B_Global_Desired[3] = self.dsb_xxGradient.value()/1000 # mT/m -> T/m
        self.B_Global_Desired[4] = self.dsb_xyGradient.value()/1000 # mT/m -> T/m
        self.B_Global_Desired[5] = self.dsb_xzGradient.value()/1000 # mT/m -> T/m
        self.B_Global_Desired[6] = self.dsb_yyGradient.value()/1000 # mT/m -> T/m
        self.B_Global_Desired[7] = self.dsb_yzGradient.value()/1000 # mT/m -> T/m
        field.isGradControlled = True
        field.setGradient(self.B_Global_Desired)

    def clearField(self):
        self.dsb_x.setValue(0)
        self.dsb_y.setValue(0)
        self.dsb_z.setValue(0)
        self.dsb_xxGradient.setValue(0)
        self.dsb_xyGradient.setValue(0)
        self.dsb_xzGradient.setValue(0)
        self.dsb_yyGradient.setValue(0)
        self.dsb_yzGradient.setValue(0)
        self.B_Global_Desired = [0]*8
        field.setXYZ(self.B_Global_Desired)
        field.setGradient(self.B_Global_Desired)
        field.isGradControlled = False
        print('Currents cleared!')

    # subthread
    def on_cbb_subThread(self,subThreadName):
        # an array that stores the name for params. Return param0, param1, ... if not defined.
        labelNames = self.thrd.labelOnGui.get(subThreadName,self.thrd.labelOnGui['default'])
        minVals = self.thrd.minOnGui.get(subThreadName,self.thrd.minOnGui['default'])
        maxVals = self.thrd.maxOnGui.get(subThreadName,self.thrd.maxOnGui['default'])
        defaultVals = self.thrd.defaultValOnGui.get(subThreadName,self.thrd.defaultValOnGui['default'])
        for i in range(5):
            targetLabel = 'lbl_subThreadParam' + str(i)
            targetSpinbox = 'dsb_subThreadParam' + str(i)
            getattr(self,targetLabel).setText(labelNames[i])
            getattr(self,targetSpinbox).setMinimum(minVals[i])
            getattr(self,targetSpinbox).setMaximum(maxVals[i])
            getattr(self,targetSpinbox).setValue(defaultVals[i])


    def on_chb_startStopSubthread(self,state):
        subThreadName = self.cbb_subThread.currentText()
        if state:
            self.cbb_subThread.setEnabled(True)
            self.thrd.setup(subThreadName)
            self.thrd.start()
            print('Subthread "{}" starts.'.format(subThreadName))
        else:
            self.cbb_subThread.setEnabled(True)
            field.setFrequency(0)
            field.setMagnitude(0)
            vision.setOrientation(None)
            vision.setSeparation(None)
            self.thrd.stop()

    def on_chb_changeSubthread(self): #use this fcn to stop current subthread
        subThreadName = self.cbb_subThread.currentText()
        if self.chb_startStopSubthread.isChecked() == True:
            self.thrd.stop()
            #print('Subthread "{}" starts.'.format(subThreadName))

    def on_chb_switchSubthread(self): #use this fcn to start new subthread
        subThreadName = self.cbb_subThread.currentText()
        if self.chb_startStopSubthread.isChecked() == True:
            time.sleep(0.1) #use time lag to achieve stop -> restart in order
            self.thrd.setup(subThreadName)
            self.thrd.start()
            print('Subthread "{}" starts.'.format(subThreadName))
