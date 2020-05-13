from PyQt5.QtGui import QPolygonF, QVector2D
from PyQt5.QtCore import QPointF, Qt

class Sector:
    def __init__(self, id, points, guide, end=False):
        super(Sector, self).__init__()
        self.id = id
        self.points = []
        for ip, p in enumerate(points):
            self.points.append(QPointF(p[0], p[1]))
        self.poly = QPolygonF(self.points)
        self.guide = QVector2D(*guide)
        #self.isLowRange = turn
        self.isFinish = end

    def isIn(self, point):
        return self.poly.containsPoint(point, Qt.OddEvenFill)