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
        self.addedDataA1 = []
        self.addedDataA2 = []
        self.addedDataA3 = []
        self.addedDataA4 = []
        self.addedDataA5 = []
        self.addedDataA6 = []
        self.addedDataA7 = []
        self.addedDataA8 = []
        self.ylimRange = [-32,32]
        self.ylimRange2 = [-24,24]
        self.isZoomed = False
        # print(matplotlib.__version__)

        # data
        self.numberOfSamplesStored = 200
        self.t = np.linspace(0, self.numberOfSamplesStored - 1, self.numberOfSamplesStored)
        self.x = (self.t * 0.0)
        self.y = (self.t * 0.0)
        self.z = (self.t * 0.0)
        self.a1 = (self.t * 0.0)
        self.a2 = (self.t * 0.0)
        self.a3 = (self.t * 0.0)
        self.a4 = (self.t * 0.0)
        self.a5 = (self.t * 0.0)
        self.a6 = (self.t * 0.0)
        self.a7 = (self.t * 0.0)
        self.a8 = (self.t * 0.0)

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
        # line3 in plot 2
        self.line23 = Line2D([], [], color='tab:red')
        self.line23_tail = Line2D([], [], color='tab:red', linewidth=2)
        self.line23_head = Line2D([], [], color='tab:red', marker='o', markeredgecolor='tab:red')
        self.ax2.add_line(copy(self.line23))
        self.ax2.add_line(copy(self.line23_tail))
        self.ax2.add_line(copy(self.line23_head))
        # line4 in plot 2
        self.line24 = Line2D([], [], color='tab:red')
        self.line24_tail = Line2D([], [], color='tab:red', linewidth=2)
        self.line24_head = Line2D([], [], color='tab:red', marker='o', markeredgecolor='tab:red')
        self.ax2.add_line(copy(self.line24))
        self.ax2.add_line(copy(self.line24_tail))
        self.ax2.add_line(copy(self.line24_head))
        # line5 in plot 2
        self.line25 = Line2D([], [], color='tab:red')
        self.line25_tail = Line2D([], [], color='tab:red', linewidth=2)
        self.line25_head = Line2D([], [], color='tab:red', marker='o', markeredgecolor='tab:red')
        self.ax2.add_line(copy(self.line25))
        self.ax2.add_line(copy(self.line25_tail))
        self.ax2.add_line(copy(self.line25_head))
        # line6 in plot 2
        self.line26 = Line2D([], [], color='tab:red')
        self.line26_tail = Line2D([], [], color='tab:red', linewidth=2)
        self.line26_head = Line2D([], [], color='tab:red', marker='o', markeredgecolor='tab:red')
        self.ax2.add_line(copy(self.line26))
        self.ax2.add_line(copy(self.line26_tail))
        self.ax2.add_line(copy(self.line26_head))
        # line7 in plot 2
        self.line27 = Line2D([], [], color='tab:red')
        self.line27_tail = Line2D([], [], color='tab:red', linewidth=2)
        self.line27_head = Line2D([], [], color='tab:red', marker='o', markeredgecolor='tab:red')
        self.ax2.add_line(copy(self.line27))
        self.ax2.add_line(copy(self.line27_tail))
        self.ax2.add_line(copy(self.line27_head))
        # line8 in plot 2
        self.line28 = Line2D([], [], color='tab:red')
        self.line28_tail = Line2D([], [], color='tab:red', linewidth=2)
        self.line28_head = Line2D([], [], color='tab:red', marker='o', markeredgecolor='tab:red')
        self.ax2.add_line(copy(self.line28))
        self.ax2.add_line(copy(self.line28_tail))
        self.ax2.add_line(copy(self.line28_head))
        #lim
        self.ax2.set_xlim(0, self.numberOfSamplesStored - 1)
        self.ax2.set_ylim(self.ylimRange[0], self.ylimRange[1])
        self.ax2.get_xaxis().set_visible(False)

        # init
        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval = 50, blit = True)

    # ========================================================
    # connected to signel callback signal
    # ========================================================
    def addDataX(self, value): self.addedDataX.append(value)
    def addDataY(self, value): self.addedDataY.append(value)
    def addDataZ(self, value): self.addedDataZ.append(value)

    def addDataA1(self, value): self.addedDataA1.append(value)
    def addDataA2(self, value): self.addedDataA2.append(value)
    def addDataA3(self, value): self.addedDataA3.append(value)
    def addDataA4(self, value): self.addedDataA4.append(value)
    def addDataA5(self, value): self.addedDataA5.append(value)
    def addDataA6(self, value): self.addedDataA6.append(value)
    def addDataA7(self, value): self.addedDataA7.append(value)
    def addDataA8(self, value): self.addedDataA8.append(value)

    def new_frame_seq(self):
        return iter(range(self.t.size))

    def _init_draw(self):
        lines = [self.line11, self.line11_tail, self.line11_head,self.line12, self.line12_tail, self.line12_head,self.line13, self.line13_tail, self.line13_head]
        lines2 = [self.line21, self.line21_tail, self.line21_head, self.line22, self.line22_tail, self.line22_head, self.line23, self.line23_tail, self.line23_head, \
        self.line24, self.line24_tail, self.line24_head, self.line25, self.line25_tail, self.line25_head, self.line26, self.line26_tail, self.line26_head, \
        self.line27, self.line27_tail, self.line27_head, self.line28, self.line28_tail, self.line28_head]
        for l in lines:
            l.set_data([], [])
        for l2 in lines2:
            l2.set_data([], [])

    def zoom(self, value):
        if self.isZoomed:
            self.ax1.set_ylim(self.ylimRange[0],self.ylimRange[1])
            self.ax2.set_ylim(self.ylimRange2[0],self.ylimRange2[1])
        else:
            self.ax1.set_ylim(self.ylimRange[0]/2,self.ylimRange[1]/2)
            self.ax2.set_ylim(self.ylimRange2[0]/2,self.ylimRange2[1]/2)
        self.draw()
        self.isZoomed = not self.isZoomed

    def _draw_frame(self, framedata):
        margin = 2
        while(len(self.addedDataX) > 0):
            self.x = np.roll(self.x, -1)
            self.y = np.roll(self.y, -1)
            self.z = np.roll(self.z, -1)
            self.a1 = np.roll(self.a1, -1)
            self.a2 = np.roll(self.a2, -1)
            self.a3 = np.roll(self.a3, -1)
            self.a4 = np.roll(self.a4, -1)
            self.a5 = np.roll(self.a5, -1)
            self.a6 = np.roll(self.a6, -1)
            self.a7 = np.roll(self.a7, -1)
            self.a8 = np.roll(self.a8, -1)
            self.x[-1] = self.addedDataX[0]
            self.y[-1] = self.addedDataY[0]
            self.z[-1] = self.addedDataZ[0]
            self.a1[-1] = self.addedDataA1[0]
            self.a2[-1] = self.addedDataA2[0]
            self.a3[-1] = self.addedDataA3[0]
            self.a4[-1] = self.addedDataA4[0]
            self.a5[-1] = self.addedDataA5[0]
            self.a6[-1] = self.addedDataA6[0]
            self.a7[-1] = self.addedDataA7[0]
            self.a8[-1] = self.addedDataA8[0]
            del(self.addedDataX[0])
            del(self.addedDataY[0])
            del(self.addedDataZ[0])
            del(self.addedDataA1[0])
            del(self.addedDataA2[0])
            del(self.addedDataA3[0])
            del(self.addedDataA4[0])
            del(self.addedDataA5[0])
            del(self.addedDataA6[0])
            del(self.addedDataA7[0])
            del(self.addedDataA8[0])
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

        self.line21.set_data(self.t[ 0 : self.t.size - margin ], self.a1[ 0 : self.t.size - margin ])
        self.line21_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.a1[-10:-1 - margin], self.a1[-1 - margin]))
        self.line21_head.set_data(self.t[-1 - margin], self.a1[-1 - margin])

        self.line22.set_data(self.t[ 0 : self.t.size - margin ], self.a2[ 0 : self.t.size - margin ])
        self.line22_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.a2[-10:-1 - margin], self.a2[-1 - margin]))
        self.line22_head.set_data(self.t[-1 - margin], self.a2[-1 - margin])

        self.line23.set_data(self.t[ 0 : self.t.size - margin ], self.a3[ 0 : self.t.size - margin ])
        self.line23_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.a3[-10:-1 - margin], self.a3[-1 - margin]))
        self.line23_head.set_data(self.t[-1 - margin], self.a3[-1 - margin])

        self.line24.set_data(self.t[ 0 : self.t.size - margin ], self.a4[ 0 : self.t.size - margin ])
        self.line24_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.a4[-10:-1 - margin], self.a4[-1 - margin]))
        self.line24_head.set_data(self.t[-1 - margin], self.a4[-1 - margin])

        self.line25.set_data(self.t[ 0 : self.t.size - margin ], self.a5[ 0 : self.t.size - margin ])
        self.line25_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.a5[-10:-1 - margin], self.a5[-1 - margin]))
        self.line25_head.set_data(self.t[-1 - margin], self.a5[-1 - margin])

        self.line26.set_data(self.t[ 0 : self.t.size - margin ], self.a6[ 0 : self.t.size - margin ])
        self.line26_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.a6[-10:-1 - margin], self.a6[-1 - margin]))
        self.line26_head.set_data(self.t[-1 - margin], self.a6[-1 - margin])

        self.line27.set_data(self.t[ 0 : self.t.size - margin ], self.a7[ 0 : self.t.size - margin ])
        self.line27_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.a7[-10:-1 - margin], self.a7[-1 - margin]))
        self.line27_head.set_data(self.t[-1 - margin], self.a7[-1 - margin])

        self.line28.set_data(self.t[ 0 : self.t.size - margin ], self.a8[ 0 : self.t.size - margin ])
        self.line28_tail.set_data(np.append(self.t[-10:-1 - margin], self.t[-1 - margin]), np.append(self.a8[-10:-1 - margin], self.a8[-1 - margin]))
        self.line28_head.set_data(self.t[-1 - margin], self.a8[-1 - margin])

        # self._drawn_artists = [self.line21, self.line21_tail, self.line21_head,self.line22, self.line22_tail, self.line22_head,self.line23, self.line23_tail, self.line23_head]
