import matplotlib
import numpy as np
from PyQt5.QtCore import pyqtSlot
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from copy import copy

class CustomFigCanvas(FigureCanvas, TimedAnimation):
    ''' A class that inherited matplotlib backend. used for plotting field value in real time. '''
    def __init__(self):
        self.addedDataX = []
        self.addedDataY = []
        self.addedDataZ = []
        # self.addedData
        self.ylimRange = [-32,32]
        self.isZoomed = False
        # print(matplotlib.__version__)

        # data
        self.numberOfSamplesStored = 200
        self.t = np.linspace(0, self.numberOfSamplesStored - 1, self.numberOfSamplesStored)
        self.x = (self.t * 0.0)
        self.y = (self.t * 0.0)
        self.z = (self.t * 0.0)
        # The window
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.fig.patch.set_facecolor((0.98, 0.98, 0.98))
        self.ax1 = self.fig.add_subplot(211,box_aspect=0.35)
        self.ax2 = self.fig.add_subplot(212,box_aspect=0.35)
        # self.ax1 settings
        self.ax1.set_title('Field XYZ (mT)',fontsize=9)
        self.ax2.set_title('Coil Currents (A)',fontsize=9)

        # line1 X in plot 1
        self.line11 = Line2D([], [], color='tab:blue')
        self.line11_tail = Line2D([], [], color='tab:blue', linewidth=2)
        self.line11_head = Line2D([], [], color='tab:blue', marker='o', markeredgecolor='tab:blue')
        self.ax1.add_line(self.line11)
        self.ax1.add_line(self.line11_tail)
        self.ax1.add_line(self.line11_head)
        # line2 Y in plot 1
        self.line12 = Line2D([], [], color='tab:green')
        self.line12_tail = Line2D([], [], color='tab:green', linewidth=2)
        self.line12_head = Line2D([], [], color='tab:green', marker='o', markeredgecolor='tab:green')
        self.ax1.add_line(self.line12)
        self.ax1.add_line(self.line12_tail)
        self.ax1.add_line(self.line12_head)
        # line3 Z in plot 1
        self.line13 = Line2D([], [], color='tab:red')
        self.line13_tail = Line2D([], [], color='tab:red', linewidth=2)
        self.line13_head = Line2D([], [], color='tab:red', marker='o', markeredgecolor='tab:red')
        self.ax1.add_line(self.line13)
        self.ax1.add_line(self.line13_tail)
        self.ax1.add_line(self.line13_head)
        #lim
        self.ax1.set_xlim(0, self.numberOfSamplesStored - 1)
        self.ax1.set_ylim(self.ylimRange[0], self.ylimRange[1])
        self.ax1.get_xaxis().set_visible(False)
        # init
        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval = 50, blit = True)


        # line1 in plot 2
        self.line21 = Line2D([], [], color='tab:blue')
        self.line21_tail = Line2D([], [], color='tab:blue', linewidth=2)
        self.line21_head = Line2D([], [], color='tab:blue', marker='o', markeredgecolor='tab:blue')
        self.ax2.add_line(copy(self.line21))
        self.ax2.add_line(copy(self.line21_tail))
        self.ax2.add_line(copy(self.line21_head))
        # line2 in plot 2
        self.line22 = Line2D([], [], color='tab:green')
        self.line22_tail = Line2D([], [], color='tab:green', linewidth=2)
        self.line22_head = Line2D([], [], color='tab:green', marker='o', markeredgecolor='tab:green')
        self.ax2.add_line(copy(self.line22))
        self.ax2.add_line(copy(self.line22_tail))
        self.ax2.add_line(copy(self.line22_head))

        self.ax2.set_xlim(0, self.numberOfSamplesStored - 1)
        self.ax2.set_ylim(self.ylimRange[0], self.ylimRange[1])
        self.ax2.get_xaxis().set_visible(False)

    # ========================================================
    # connected to signel callback signal
    # ========================================================
    def addDataX(self, value): self.addedDataX.append(value)
    def addDataY(self, value): self.addedDataY.append(value)
    def addDataZ(self, value): self.addedDataZ.append(value)

    def new_frame_seq(self):
        return iter(range(self.t.size))

    def _init_draw(self):
        lines = [self.line11, self.line11_tail, self.line11_head,self.line12, self.line12_tail, self.line12_head,self.line13, self.line13_tail, self.line13_head]
        for l in lines:
            l.set_data([], [])

    def zoom(self, value):
        if self.isZoomed:
            self.ax1.set_ylim(self.ylimRange[0],self.ylimRange[1])
        else:
            self.ax1.set_ylim(self.ylimRange[0]/2,self.ylimRange[1]/2)
        self.draw()
        self.isZoomed = not self.isZoomed

    def _draw_frame(self, framedata):
        margin = 2
        while(len(self.addedDataX) > 0):
            self.x = np.roll(self.x, -1)
            self.y = np.roll(self.y, -1)
            self.z = np.roll(self.z, -1)
            self.x[-1] = self.addedDataX[0]
            self.y[-1] = self.addedDataY[0]
            self.z[-1] = self.addedDataZ[0]
            del(self.addedDataX[0])
            del(self.addedDataY[0])
            del(self.addedDataZ[0])
        self.line11.set_data(self.t[ 0 : self.t.size - margin ], self.x[ 0 : self.t.size - margin ])
        self.line11_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.x[-10:-1 - margin], self.x[-1 - margin]))
        self.line11_head.set_data(self.t[-1 - margin], self.x[-1 - margin])

        self.line12.set_data(self.t[ 0 : self.t.size - margin ], self.y[ 0 : self.t.size - margin ])
        self.line12_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.y[-10:-1 - margin], self.y[-1 - margin]))
        self.line12_head.set_data(self.t[-1 - margin], self.y[-1 - margin])

        self.line13.set_data(self.t[ 0 : self.t.size - margin ], self.z[ 0 : self.t.size - margin ])
        self.line13_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.z[-10:-1 - margin], self.z[-1 - margin]))
        self.line13_head.set_data(self.t[-1 - margin], self.z[-1 - margin])

        self._drawn_artists = [self.line11, self.line11_tail, self.line11_head,self.line12, self.line12_tail, self.line12_head,self.line13, self.line13_tail, self.line13_head]
