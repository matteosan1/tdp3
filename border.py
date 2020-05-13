import math

from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QPointF, QRectF, Qt, QLineF
from PyQt5.QtGui import QPen, QBrush, QVector2D

def getAngle(v):
    if v.dx() == 0:
        v_angle = math.degrees(math.atan(v.dy() / abs(v.dy()) * math.inf))
    else:
        v_angle = math.degrees(math.atan(v.dy() / v.dx()))
        #print ("tmp vangle ", v_angle)
        if v.dx() < 0:
            if v_angle <= -90:
                v_angle = 180 + v_angle
            elif v_angle <= 90:
                v_angle = v_angle - 180

    return v_angle

def collisionAngle2(l, v, radius=20):
    xc, yc = v.x1(), v.y1()
    #print(l)
    norm = l.normalVector()
    x1, x2, y1, y2 = l.x1(), l.x2(), l.y1(), l.y2()
    #print(y1, y2)
    #if x1 == x2:
        # b = -2 * yc
        # c = (x1 - xc) ** 2 + yc * yc - radius * radius
        # print(b, c)
        # delta = b * b - 4 * c
        # if delta < 0:
        #     return None
        # yi = -b / (2 * a)
        # print("delta ", delta)
        # print("Yi ", yi, y1, y2)
        # if y1 <= yi <= y2:
        #     print("lines ", l)
        #     print ("lines2 ", v)
        #     print ("lines3", l.normalVector())
        #     return v.angleTo(l.normalVector())
        #     # FIXME nel caso degli spigoli
    #else:
    #print("lines ", l, v, norm)
    v_angle = getAngle(v)
    norm_angle = getAngle(norm)
    #print (v_angle, norm_angle)
    diff = v_angle - norm_angle
    new_direction = norm_angle - diff
    return math.radians(new_direction)

class Border(QGraphicsItem):
    #def __init__(self, x, y, width, height, vx, vy):
    def __init__(self, x1, y1, x2, y2, dir):
        super(Border, self).__init__()
        #self.pos = QPointF(x, y)
        #self.lines = [QLineF(x, y, x + width, y),
        #              QLineF(x, y, x, y + height),
        #              QLineF(x, y + height, x + width, y + height),
        #              QLineF(x + width, y, x + width, y + height)]
        #self.width = width
        #self.height = height
        #self.rect = QRectF(self.pos.x(), self.pos.y(), self.width, self.height)
        if dir == 1:
            self.line = QLineF(x1, y1, x2, y2)
        else:
            self.line = QLineF(x2, y2, x1, y1)

        #self.direction = QVector2D(vx, vy)

    def type(self):
        return QGraphicsItem.UserType + 1

    # def collisionAngle(self, line):
    #     intersects = (None, 0)
    #     for l in self.lines:
    #         r = line.intersects(l)
    #         print (r, l, line)
    #         if r[0] == 1:
    #             tmp = QLineF(line.p1(), r[1])
    #             if intersects[0] is None or tmp.length() < intersects[1]:
    #                 print ("raggio ", tmp, tmp.length()) # corretto
    #                 print ("l ", l, tmp.angleTo(l))
    #                 print ("l_perp ", l.normalVector(), tmp.angleTo(l.normalVector()))
    #                 intersects = [tmp, tmp.length(), tmp.angleTo(l.normalVector())]
    #                 print ("inter ", intersects)
    #
    #     if intersects[0] is not None:
    #         return intersects[2]
    #     else:
    #         return 0

    def boundingRect(self):
        #return QRectF(self.pos.x(), self.pos.y(), self.width, self.height)
        return QRectF(self.line.x1(), self.line.y1(), self.line.dx()+2, self.line.dy()+2)

    def paint(self, painter, option, widget):
        #painter.setRenderHint(QPainter::Antialiasing);
        #painter.setPen(Qt::black);
        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.red, Qt.VerPattern))
        painter.drawLine(self.line)