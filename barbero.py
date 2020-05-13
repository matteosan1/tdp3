import math
from random import randint

from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPixmap, QVector2D, QPainterPath, QPen
from PyQt5.QtCore import QRectF, QLineF, QPointF, Qt, QObject, pyqtSignal

from border import collisionAngle2, getAngle

def compare(b1, b2):
    if b1.currentSector < b2.currentSector:
        return -1
    elif b1.currentSector > b2.currentSector:
        return 1
    else:
        if b1.distToTarget() > b2.distToTarget():
            return -1
        else:
            return 1

class Barbero(QGraphicsItem):
    RADIUS = 40
    FRICTION = 0.3 * 9.8
    ABSORPTION = 0.9
    dt = 0
    #move_ended = pyqtSignal()

    def __init__(self, id, x0, y0):
        super(Barbero, self).__init__()
        self.currentSector = 0
        self.currentFrame = 99
        self.isHuman = False
        self.cavallo = None
        self.fantino = None
        self.pos = QVector2D(x0, y0)
        self.setPos(self.pos.toPointF())
        self.v = QVector2D(0, 0)
        self.steps = 0
        self.path_x = []
        self.path_y = []
        self.id = id
        self.spriteImage = QPixmap(":/images/" + self.id.lower() + ".png")
        self.boundRect = QRectF(-20, -20, self.RADIUS, self.RADIUS)
        self.boundPath = QPainterPath()
        self.boundPath.addEllipse(QPointF(0, 0), 20, 20)
        self.dt = 0.1
        self.min_dist = None

    def type(self):
        return QGraphicsItem.UserType + 2

    def distToTarget(self):
        dist = self.pos.distanceToPoint(self.target)
        return dist

    # FIXME fare un oggetto settori come container dei settori
    # a cui aggiungere una funzione per sapere dove sono i barberi
    def findTarget(self, sectors):
        for iSector, s in enumerate(sectors):
            if s.isIn(self.pos.toPointF()):
                self.currentSector = iSector

        #smax = 0.5 * (self.cavallo.vmax ** 2) / self.FRICTION
        smax = 0.5 * (randint(40, 50) ** 2) / self.FRICTION
        #print ("smax ", smax, self.currentSector)
        #print (self.currentSector)

        # if sectors[self.currentSector].isLowRange:
        #     print ("low")
        #     target = sectors[self.currentSector+1].guide
        # else:
        #     iSector = self.currentSector + 1
        #     print (iSector)
        #     if sectors[self.currentSector].isFinish:
        #         print ("next is finished")
        #         target = sectors[iSector].guide
        #     else:
        #         while iSector < (len(sectors)):
        #             print ("loop isector {}".format(iSector))
        #             dist = self.pos.distanceToPoint(QVector2D(sectors[iSector].guide))
        #             if dist > smax or sectors[iSector].isLowRange or sectors[iSector].isFinish:
        #                 target = sectors[iSector].guide
        #                 break
        #             iSector += 1
        self.target = sectors[self.currentSector].guide
        #angle = math.degrees(math.acos(QVector2D.dotProduct(self.pos.normalized(), target.normalized())))
        angle = 360 - QLineF(self.pos.toPointF(), self.target.toPointF()).angle()

        lrange = -85
        hrange = 85
        if angle > 90 and angle < 270:
            lrange = -265
            hrange = -85

        return smax, lrange, hrange

    def chooseMove(self, init_position, sectors, borders=None):
        smax, lrange, hrange = self.findTarget(sectors)

        best_path = None
        #print ("target", target)
        #print (angle)

        steps = 5
        # FIXME se il fantino e` preciso fare uno scan ulteriore
        # intorno a +- 2.5 gradi dal best (da valutare con semaring dovuto al cavallo)
        for anAngle in range(lrange, hrange, steps):
            collisions = 0
            origin = QVector2D(self.pos.x(), self.pos.y())
            min_dist = origin.distanceToPoint(self.target)
            current_best = [min_dist, 0, origin, anAngle]
            #print("Angolo", anAngle, origin)
            path = QPainterPath()
            path.addEllipse(origin.toPoint(), 20, 20)
            dv = QVector2D(math.cos(math.radians(anAngle)), math.sin(math.radians(anAngle)))
            #print ("dV", dv)
            #print ("orig", origin)
            # for it in self.scene().items():
            #     if it.type() == QGraphicsItem.UserType + 2:
            #         if it == self:
            #             continue
            #         print (it.boundingRect())
            #         pen = QPen(Qt.red, 5, Qt.SolidLine)
            #         self.scene().addPath(it.shape(), pen)
            #         if path.intersects(it.shape()):
            #             print("COLLISION ", it.id)
            # return

            iterS = 0
            while iterS <= int(smax):
            #for i in range(int(smax)):
                origin += dv
                #print ("origin", iterS, origin)
                path.moveTo(origin.toPoint())

                for it in self.scene().items():
                    if it.type() == QGraphicsItem.UserType + 2:
                        if it == self:
                            continue
                        if path.intersects(it.mapToScene(it.shape())):
                            collisions += 1
                            #print ("COLLISION ", it.id)
                            r = QVector2D(it.pos.x() - origin.x(), it.pos.y() - origin.y()).normalized()
                            cos_theta = QVector2D.dotProduct(dv, r)
                            dv_mod_squared = (smax - iterS) * 2 * self.FRICTION * cos_theta * cos_theta
                            #print ("before ", iterS, dv_mod_squared)
                            #print (cos_theta, r)
                            dv_coll = cos_theta * r
                            dv -= dv_coll
                            origin += dv
                            iterS += 0.5 * dv_mod_squared / self.FRICTION
                            #print ( "after ", iterS, smax)
                            #print ("new dv ", dv)
                            break

                # FIXME loop solo sui bordi associati al settore
                for ib, b in enumerate(borders):
                    #FIXME riduci velocita in caso di urto
                    #print ("border ", ib)
                    if path.intersects(b.boundingRect()):
                        #print ("Collision ", ib)
                        new_angle = collisionAngle2(b.line, QLineF((origin+22*dv).toPointF(), origin.toPointF()))
                        #print ("NEW ANGLE ", new_angle)
                        dv = QVector2D(math.cos(new_angle), math.sin(new_angle))
                        #cos_theta = abs(math.cos(math.radians(angle)))
                        #print("angle after: ", angle, cos_theta)

                        # simulare perdita di energia nel rimbalzo
                        #print ("intersect with:", ib, path.currentPosition())
                        #cos_theta = QVector2D.dotProduct(b.direction, dv)
                        #print ("angle after: ", math.degrees(math.acos(cos_theta)))
                        #dv -= 2 * dv * cos_theta
                        #dv = dv.normalized()
                        #print ("dv ", dv)
                        origin += dv
                        break
                #print (collisions)
                tmp_dist = origin.distanceToPoint(self.target) #+ collisions * 200
                #print (tmp_dist)
                if tmp_dist < min_dist:
                    min_dist = tmp_dist
                    current_best = [min_dist, iterS, origin, anAngle]
                    #print (current_best)
                iterS += 1

            #current_best[0] += 0.5*origin.distanceToPoint(sectors[self.currentSector+1].guide)
            sect = -1
            for iSector, s in enumerate(sectors):
                if s.isIn(origin.toPointF()):
                    sect = iSector
                    break
            me = [sect, origin.distanceToPoint(sectors[sect+1].guide)]
            overtakes = 0
            for it in self.scene().items():
                if it == self:
                    continue
                if it.type() == QGraphicsItem.UserType + 2:
                    sect = -1
                    for iSector, s in enumerate(sectors):
                        if s.isIn(origin.toPointF()):
                            sect = iSector
                            break
                    if sect < me[0]:
                        overtakes += 1
                    elif sect == me[0]:
                        dist = it.pos.distanceToPoint(sectors[sect+1].guide)
                        if dist > me[1]:
                            overtakes += 1
            # FIXME modulare questo numero in base alla posizione
            # se e` dietro se ne frega delle collisioni
            delta = - collisions * 100
            print (delta)
            if (10 - overtakes) < init_position:
                delta += (init_position - 10 + overtakes) * 20
                print (delta)

            current_best[0] -= delta
            print ("{}".format(self.id), current_best, self.target, origin)
            if best_path is None:
                best_path = current_best
            else:
                if current_best[0] < best_path[0]:
                    best_path = current_best
                elif abs(current_best[0] - best_path[0])/current_best[0] < 0.05:
                    if current_best[1] < best_path[1]:
                        best_path = current_best

        # salva il percorso con minore distanza dalla guida (poi aggiungere la distanza anche dal prossimo punto)
        #                       minore spazio percorso
            #self.scene().addLine(QLineF(self.pos.x(), origin.x(), self.pos.y(), origin.y()))
        #speed = 40
        #direction = -85
        print ("BEST ", best_path)
        speed = math.sqrt(2*best_path[1]*self.FRICTION)
        #print (speed)
        #self.min_dist = best_path[0]
        # FIXME errore casuale gaussiano in base alla precisione
        # del cavallo
        self.initKinematics(best_path[3], speed)

    def move(self, sectors):
        #print ("{} {}".format(self.id, (self.v.length())))
        if self.v.length() < 3.5:
            self.v = QVector2D()
            #self.scene().move_ended.emit()
            return
            #print ("{} non si muove".format(self.id))
            #return
        #else:
        #    print ("{} v: {}".format(self.id, self.v.length()))

        #smax = self.v.length() * self.dt
        #orig_pos = self.pos
        steps = 1
        self.setRotation(math.degrees(math.atan2(self.v.y(), self.v.x())))

        for _ in range(steps):
            ds = self.v * self.dt / steps
            newpos = self.pos + ds
            items = self.scene().collidingItems(self)
            #print ("COLLISIONI ", len(items), newpos)
            if len(items) != 0:
                for it in items:
                    if it.type() == QGraphicsItem.UserType + 1:
                        tmp = (self.pos + 22*self.v.normalized())
                        test = QLineF(tmp.x(), tmp.y(), self.pos.x(), self.pos.y())
                        #print ("test", test)
                        new_angle = collisionAngle2(it.line, test)
                        #cos_theta = abs(math.cos(math.radians(angle)))
                        #self.v -= 2 * self.v * cos_theta
                        self.v = self.v.length() * QVector2D(math.cos(new_angle), math.sin(new_angle))
                        ds = self.v * self.dt / steps
                        newpos = self.pos + ds
                        break
                    elif it.type() == QGraphicsItem.UserType + 2:
                        #print ("COLLISION ", it.id)
                        r = QVector2D(it.pos.x() - self.pos.x(), it.pos.y() - self.pos.y()).normalized()
                        cos_theta = QVector2D.dotProduct(self.v.normalized(), r)
                        #print (cos_theta, r, self.v)
                        if cos_theta > 0:
                            #self.setRotation(math.degrees(new_angle))
                            delta_v = self.v.length() * cos_theta * r
                            self.v -= delta_v
                            it.v += delta_v
                            newpos = it.pos + it.v * self.dt/steps
                            it.setPos(newpos.toPointF())
                            ds = self.v * self.dt / steps
                            newpos = self.pos + ds

            #print ("POST BREAK")
            self.currentFrame -= int(ds.length())
            if self.currentFrame < 0:
                self.currentFrame = 99 #self.currentFrame % 100
            self.update(0, 0, self.RADIUS, self.RADIUS)

            self.pos = newpos
            #print (newpos)
            self.setPos(self.pos.toPoint()) #self.mapToParent(0, -(3 + math.sin(self.speed) * 3)))

        #print ("deltaV ", self.dt * self.FRICTION / steps)
        self.v -= self.v.normalized() * self.dt * self.FRICTION / steps
        if self.v.length() < 3.5:
            self.v = QVector2D()
            self.scene().move_ended.emit()

        if sectors[self.currentSector + 1].isIn(self.pos.toPointF()):
            self.currentSector += 1
            self.target = sectors[self.currentSector].guide
            print ("TARGET SET ", self.target)
        if sectors[self.currentSector].isFinish:
            self.scene().race_ended.emit(self.id)

    def initKinematics(self, direction, speed, dt=0.1):
        self.dt = dt
        #self.setRotation(direction)
        #print ("premove", speed, direction)
        angle = math.radians(direction)
        v0 = QVector2D(speed * math.cos(angle), speed * math.sin(angle))
        self.v += v0
        #self.steps = int((abs(self.v.lemght()) / FRICTION) / self.dt)
        #print ("Number of steps for {}, {}".format(self.id, self.steps))

    # def checkWalls(self, wall, dt):
    #     m = self.v.m()
    #     m_w = (wall['coord'][3] - wall['coord'][1])/(wall['coord'][2] - wall['coord'][0])
    #     if m == m_w: # direction is perp to the wall
    #         return
    #     x_i = (m_w * wall['coord'][0] - m * self.pos.x + self.pos.y - wall['coord'][1])/(m_w - m)
    #     y_i = m * x_i + (self.pos.y - m * self.pos.x)
    #
    #     d = math.sqrt(math.pow(self.pos.x - x_i, 2) + math.pow(self.pos.y - y_i, 2))
    #     # distanza da retta (bordo)
    #
    #     # se distanza minore dello spazio percorso in dT (collisione)
    #
    #     frac = d / (self.v.mod() * dt)
    #     print("v", self.v.x, self.v.y, self.v.mod())
    #     if frac < 1. and self.v.y*wall['diry'] < 0:
    #         self.updatePos(d/self.v.mod())
    #         if m_w == 0:
    #             m_perp = 1e10
    #         else:
    #             m_perp = -1/m_w
    #         print (m_perp)
    #         v_perp = -2 * self.v.proj(m_perp)
    #         print (v_perp)
    #         print (math.degrees(math.atan(m_perp)))
    #         self.v.sumWithDirection(v_perp * ABSORPTION, math.degrees(math.atan(m_perp)))
    #         print ("v", self.v.x, self.v.y, self.v.mod())
    #         self.steps = int((self.v.mod() / FRICTION) / dt)
    #         #return True
    #     #else:
    #     #    return True
    #
    # def dmove(self, border, barberi, dt=0.1):
    #     if self.steps > 0:
    #         print ("STEP", self.steps)
    #         #print ("dir:", direction)
    #         self.updateSpeed(dt)
    #         coll = self.checkCollisions(barberi, dt)
    #         if coll is not None:
    #             collision(*coll)
    #             return True
    #         #self.checkWalls(border[1], dt)
    #         self.updatePos(dt)
    #         self.steps -= 1
    #         #print (self.point_x)
    #         return True
    #     return False

    def boundingRect(self):
        return self.boundRect

    def shape(self):
        return self.boundPath

    def paint(self, painter, option, widget):
        ix = 9 - (self.currentFrame % 10)
        #ix = self.currentFrame % 10
        iy = self.currentFrame // 10
        #iy = 9 - self.currentFrame // 10
        #print(self.currentFrame, ix, iy)
        painter.drawPixmap(-20, -20, self.spriteImage, ix*self.RADIUS, iy*self.RADIUS, self.RADIUS, self.RADIUS)

    def nextFrame(self):
        self.currentFrame += 1
        if self.currentFrame >= 100:
            self.currentFrame = 0
        self.update(0, 0, self.RADIUS, self.RADIUS)
        #self.move()
