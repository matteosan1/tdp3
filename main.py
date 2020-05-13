import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from PyQt5.QtMultimedia import QSound

from mainwindow import Ui_MainWindow
from simulation import Simulation
from manager import TdPManager

import tdp_rc

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.button_pushed)

        self.manager = TdPManager()
        self.manager.estrazione()
        self.simulation = Simulation(self.manager.corrono,
                                     self.ui.graphicsView,
                                     self.ui.pushButton2,
                                     self.ui.verticalSlider)

    def button_pushed(self):
        self.simulation.start = True
        self.simulation.run()

    # FIXME impostare il loop dell'annata per ora con semplici
    # printout, pui si traduce in grafica

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
