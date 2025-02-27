import numpy as np
import cv2, sys, os, time
# from objectDetection import drawContour

class Vision2(object):
    def __init__(self,field):
        self.field = field
        self.cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
        if (self.cap.isOpened() == False):
            self.cap = cv2.VideoCapture("NoInput.mp4")
            self.frameCounter = 0
            self.mode = "Video"
        else:
            self.mode = "Camera"

        cv2.namedWindow(self.windowName(),16)
        cv2.moveWindow(self.windowName(), 0, 510)
        cv2.resizeWindow(self.windowName(), 640,480)

        self._isGrayscale = False
        self._isThresholdRunning = False
        self._isObjectDetectionRunning = False
        self._isFilterBlueRunning = False
        self.threshold = None
        self.maxval = None
        self.cnt_routing = np.zeros((0,2),dtype=np.uint8)
        self.state = 0
        self.firstFrameNo = None
        self.snapshotState = False
        self.videoWritingState = False

    def updateFrame(self):
        if self.mode == 'Video':
            ret, frame = self.cap.read()

            self.frameCounter += 1
            #If the last frame is reached, reset the capture and the frame_counter
            if self.frameCounter == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                self.frameCounter = 0 #Or whatever as long as it is the same as next line
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            if self.isThresholdRunning():
                grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                filteredFrame = self.runThreshold(grayFrame)
                cv2.imshow(self.windowName(),filteredFrame)
                shownFrame = filteredFrame
            elif self.isGrayscale():
                grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cv2.imshow(self.windowName(),grayFrame)
                shownFrame = grayFrame
            else:
                cv2.imshow(self.windowName(),frame)
                shownFrame = frame
            if self.snapshotState:
                timestr = time.strftime("%Y%m%d%H%M%S")
                cv2.imwrite(os.getcwd()+'/snapshot/snapshot_cam2_'+timestr+'.png',shownFrame)
                self.snapshotState = False
            if self.videoWritingState:
                self.videoWriter.write(shownFrame)

        else:
            ret, frame = self.cap.read()
            # self.frameCounter += 1
            # print(time.time() - self.startingTime,self.frameCounter)

            if self.isThresholdRunning():
                grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                filteredFrame = self.runThreshold(grayFrame)
                cv2.imshow(self.windowName(),filteredFrame)
                shownFrame = filteredFrame
            elif self.isGrayscale():
                grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cv2.imshow(self.windowName(),grayFrame)
                shownFrame = grayFrame
            else:
                cv2.imshow(self.windowName(),frame)
                shownFrame = frame
            if self.snapshotState:
                timestr = time.strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(os.getcwd()+'/snapshot/snapshot_cam2_'+timestr+'.png',shownFrame)
                self.snapshotState = False
            if self.videoWritingState:
                self.videoWriter.write(shownFrame)

    def windowName(self):
        return 'Camera2'

    def getFrameRate(self):
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        return self.fps

    def isGrayscale(self):
        return self._isGrayscale

    def isThresholdRunning(self):
        return self._isThresholdRunning

    def setOriginal(self):
        self._isGrayscale = False
        self._isThresholdRunning = False
        self.cnt_routing = np.zeros((0,2),dtype=np.uint8)
        self.state = 0
        self.firstFrameNo = None

    def setGrayscale(self):
        self._isGrayscale = True
        self._isThresholdRunning = False

    def setThreshold(self,threshold,maxval):
        self.threshold = threshold
        self.maxval = maxval
        self._isThresholdRunning = True

    def runThreshold(self,inputImage):
        _, ret = cv2.threshold(inputImage,self.threshold,self.maxval,cv2.THRESH_BINARY)
        return ret

    def setSnapshot(self):
        self.snapshotState = True

    #==============================================================================================
    # Video recording
    #==============================================================================================

    def startRecording(self):
        timestr = time.strftime("%Y%m%d_%H%M%S")
        if self.mode == 'Camera':
            self.videoWriter = cv2.VideoWriter(os.getcwd()+'/video/'+'Camera2'+'_'+timestr+'.avi',fourcc=cv2.VideoWriter_fourcc(*'MJPG'),fps=30,\
                            frameSize=(int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),isColor=True)
        else:
            self.videoWriter = cv2.VideoWriter(os.getcwd()+'/video/'+'Camera2'+'_'+timestr+'.avi',fourcc=cv2.VideoWriter_fourcc(*'MJPG'),fps=self.cap.get(cv2.CAP_PROP_FPS),\
                            frameSize=(int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),isColor=True)
        # to keep coincidence with the initial frame rate, we can use "fps=self.cap.get(cv2.CAP_PROP_FPS)"
        # the initial frame rate of camera is 120.1fps
        self.setVideoWritingEnabled(True)
        print('Start recording '+'Camera2'+'_'+timestr+'.avi...')

    def stopRecording(self):
        self.setVideoWritingEnabled(False)
        self.videoWriter.release()
        print('Stop recording.')

    def setVideoWritingEnabled(self,state):
        self.videoWritingState = state

    def close(self):
        self.cap.release()
        cv2.destroyWindow("Camera2")
