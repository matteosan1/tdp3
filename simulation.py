import json, math

from functools import cmp_to_key

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt5.QtGui import QBrush, QPixmap, QPainter, QPolygonF, QBrush, QPen
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import QObject, QLineF, QTimer, pyqtSignal, pyqtSlot, Qt, QRectF, QPointF

from barbero import Barbero, compare
#from human import HumanInterface
from border import Border
from sector import Sector

class GraphicsScene(QGraphicsScene):
    xlim = 800
    ylim = 1800
    race_ended = pyqtSignal(str)
    move_ended = pyqtSignal()
    setting_direction = pyqtSignal(int, int)

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.setSceneRect(0, 0, self.xlim, self.ylim)
        self.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.humanPlaying = False

    # FIXME da togliere alla fine
    def setPista(self, pista):
        self.pista = pista

    def mousePressEvent(self, event):
        if not self.humanPlaying:
            return

        x = event.scenePos().x()
        y = event.scenePos().y()
        print ("MOUSE POS:", x, y)
        self.setting_direction.emit(x, y)
        # for p in self.pista:
        #      pen = QPen(Qt.black, 5, Qt.SolidLine)
        #      brush = QBrush(Qt.red, Qt.VerPattern)
        #      self.addPolygon(p.poly, pen, brush)
        #
        # for p in self.pista:
        #     pen = QPen(Qt.black, 5, Qt.SolidLine)
        #     brush = QBrush(Qt.red, Qt.VerPattern)
        #     self.addEllipse(p.guide.x(), p.guide.y(), 5, 5, pen, brush)

    def removeLine(self):
        items = self.items()
        for it in items:
            if it.type() == 6:
                self.removeItem(it)

    def removeHighlight(self):
        items = self.items()
        for it in items:
            if it.type() == 4:
                self.removeItem(it)

    def highlightPlayer(self, x0, y0):
        pen = QPen(Qt.green, 6, Qt.SolidLine)
        self.addEllipse(x0 - 20, y0 - 20, 40, 40, pen)

    @pyqtSlot(int, int, int, int, int)
    def drawDirection(self, x0, y0, xp, yp, isok):
        self.removeLine()
        if isok == 1:
            pen = QPen(Qt.green, 8, Qt.DashLine)
        else:
            pen = QPen(Qt.red, 8, Qt.DashLine)
        self.addLine(QLineF(x0, y0, xp, yp), pen)


class Simulation(QObject):
    init_move_done = pyqtSignal()
    make_move = pyqtSignal()
    drawDirection = pyqtSignal(int, int, int, int, int)

    def __init__(self, corrono, view, button, slider):
        super(QObject, self).__init__()
        self.scene = GraphicsScene()
        self.view = view
        self.view.setScene(self.scene)
        self.view.scale(.65, -.65)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setBackgroundBrush(QBrush(QPixmap(':/images/tufo.png')))
        self.view.setCacheMode(QGraphicsView.CacheBackground)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setDragMode(QGraphicsView.NoDrag) #ScrollHandDrag)
        self.view.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.view.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.view.setWindowTitle("Tempo di Palio III")

        self.slider = slider
        self.slider.setMinimum(0)
        self.slider.setMaximum(50)

        self.button = button
        self.button.clicked.connect(self.button_pushed)

        self.human = "Lupa"

        self.timer = QTimer()
        self.timer.setInterval(25)
        self.timer.timeout.connect(self.moveBarberi)

        self.scene.move_ended.connect(self.checkVelocities)
        self.scene.race_ended.connect(self.fineCorsa)
        self.scene.setting_direction.connect(self.setHumanDirection)

        self.drawDirection.connect(self.scene.drawDirection)

        self.mortaretto = QSound("mortaretto.wav")
        self.iBarbero = -1
        self.start = False
        #self.ordine = range(10)

        self.drawPista()

        # init mossa
        self.barberi = []
        for ic, c in enumerate(corrono):
            #if ic > 0:
                #continue
            # FIXME posizione dx casuale (-20, 20)
            self.barberi.append(Barbero(c, 50 - ic * 2, 1380 + ic * 43))
            if c == self.human:
                self.barberi[-1].isHuman = True
            #self.barberi.append(Barbero(corrono[2], 747.0, 1325)) #1250.0)) #360.0, 850.0))
            self.scene.addItem(self.barberi[-1])
            #self.barberi.append(Barbero(corrono[3], 687.0, 1300))  # 1250.0)) #360.0, 850.0))
            #self.scene.addItem(self.barberi[-1])

    @pyqtSlot()
    def button_pushed(self):
        self.scene.humanPlaying = True
        self.scene.removeLine()
        self.scene.removeHighlight()
        self.button.setEnabled(False)
        self.barberi[self.iBarbero].initKinematics(self.human_direction, self.slider.value())
        self.timer.start()

    @pyqtSlot(int, int)
    def setHumanDirection(self, x, y):
        dx = x - self.barberi[self.iBarbero].pos.x()
        dy = y - self.barberi[self.iBarbero].pos.y()
        base = 5
        self.human_direction = base * round(math.degrees(math.atan2(dy, dx))/5)
        smax, lrange, hrange = self.barberi[self.iBarbero].findTarget(self.sectors)

        if lrange < self.human_direction < hrange:
            isok = 1
            self.button.setEnabled(True)
        else:
            isok = -1
            self.button.setEnabled(False)

        self.drawDirection.emit(self.barberi[self.iBarbero].pos.x(),
                                self.barberi[self.iBarbero].pos.y(),
                                x, y, isok)

    def drawPista(self):
        self.sectors = []
        for s in json.load(open("pista.json")):
            self.sectors.append(Sector(**s))
        # FIXME to remove after testing
        self.scene.setPista(self.sectors)

        self.borders = []
        tmp = json.load(open("bordi.json"))

        for b in tmp:
            border = Border(*b)
            self.scene.addItem(border)
            self.borders.append(border)

    @pyqtSlot()
    def run(self):
        if not self.start:
            return
        # FIXME aggiungere penalty casuale alle mossa
        # dipendente dalla prontezza del fantino
        # alla rincorsa niente per definizione
        self.iBarbero += 1
        if self.iBarbero == len(self.barberi):
            self.iBarbero = 0
            #sorted(self.barberi, key=compare)
            self.barberi = sorted(self.barberi, key=cmp_to_key(compare), reverse = True)
            print ("ordinamento ")
            for b in self.barberi:
                print (b.id, b.currentSector, b.distToTarget())

        # cambia vista per centrarla
        # x0 = max(0, self.barberi[self.iBarbero].pos.x() - 235)
        # x1 = x0 + 470
        # y1 = min(1800, self.barberi[self.iBarbero].pos.y() + 205)
        # y0 = y1 - 405
        #print (x0, x1, y0, y1)
        # if x0 < 0:
        #     x0 = 0
        #     x1 = 470
        # elif x1 > self.scene.xlim:
        #     x1 = self.scene.xlim
        #     x0 = x1 - 470
        #
        # if y0 < 0:
        #     y0 = 0
        #     y1 = 410
        # elif y1 > self.scene.ylim:
        #     y1 = self.scene.ylim
        #     y0 = y1 - 410
        #self.scene.setSceneRect(x0, y0, x1, y1)

        # scegli il path migliore o definisci velocita direzione se umano
        if not self.barberi[self.iBarbero].isHuman:
            self.barberi[self.iBarbero].chooseMove(self.iBarbero, self.sectors, self.borders)
            self.timer.start()
        else:
            self.scene.humanPlaying = True
            self.scene.highlightPlayer(self.barberi[self.iBarbero].pos.x(),
                                       self.barberi[self.iBarbero].pos.y())
            self.button.setEnabled(True)

    @pyqtSlot(str)
    def fineCorsa(self, vincitore):
        self.timer.stop()
        print ("Il Palio e` stato vinto da {}".format(vincitore))
        #sound = QSound("mortaretto.wav")
        self.mortaretto.play()
        # raccogli informazioni necessarie e passale a chi deve aggioranre statistiche
        # ovvero al manager
        # vittorie contrada, fantino, cavallo
        # eventuali aggiornamenti a fantini cavalli e contrade (infortuni, miglioramenti...)
        # partiti fatti e mantenuti

    @pyqtSlot()
    def moveBarberi(self):
        for it in self.scene.items():
            if it.type() == QGraphicsItem.UserType + 2:
                it.move(self.sectors)

    @pyqtSlot()
    def checkVelocities(self):
        print ("CHECK SPEED")
        move = False
        for b in self.barberi:
            #print ("Vel:", b.v.length())
            if b.v.length() > 0.1:
                move = True
                break

        if not move:
            self.timer.stop()
            print (self.barberi[self.iBarbero].pos)
            #self.run()

