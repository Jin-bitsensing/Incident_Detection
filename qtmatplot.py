from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):

    def __init__(self):
        self.fig, self.ax = plt.subplots()
        plt.tight_layout()
        self.ax.format_coord = format_coord

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class MatplotWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.naviToolbar = NavigationToolbar(self.canvas, self)
        self.vbl = QtGui.QGridLayout()
        self.vbl.addWidget(self.canvas, 0, 0, 1, 1)
        self.vbl.addWidget(self.naviToolbar)
        self.setLayout(self.vbl)



def format_coord(x, y):
    col = int(x + 0.5)
    row = int(y + 0.5)

    # return 'x=%1d, y=%1d' % (col, row)
    return 'R=%1d, D=%1d' % (col, row)
