# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 23:35:16 2017

@author: nnolde
"""
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QApplication

from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsPointXY,
                       QgsRectangle,
                       QgsWkbTypes)
from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsRubberBand

import os.path

# Find cursor icon in plugin tree
def resolve(name, basepath=None):
    if not basepath:
      basepath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basepath, name)
    

class PointTool(QgsMapTool):   
    def __init__(self, canvas, button):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas    
        self.button = button
        self.imgdir = resolve('icon_locate.png')
        self.cursor = QCursor(QPixmap(self.imgdir).scaledToWidth(24), 12, 12)
        
        #QApplication.setOverrideCursor(QCursor(QPixmap('/icon_locate.png')))
    
    canvasClicked = pyqtSignal(['QgsPointXY', 'QString', 'Qt::MouseButton'])
    def canvasReleaseEvent(self, event):
        #Get the click and emit a transformed point
        
        # mapSettings() was only introduced in QGIS 2.4, keep compatibility
        try:
            crsSrc = self.canvas.mapSettings().destinationCrs()
        except:
            crsSrc = self.canvas.mapRenderer().destinationCrs()
            
        crsWGS = QgsCoordinateReferenceSystem(4326)
    
        point_oldcrs = self.toMapCoordinates(event.pos())
        
        xform = QgsCoordinateTransform(crsSrc, crsWGS, QgsProject.instance())
        point_newcrs = xform.transform(point_oldcrs)
        
        QApplication.restoreOverrideCursor()
        
        self.canvasClicked.emit(point_newcrs, self.button, event.button())
        
    def activate(self):
        QApplication.setOverrideCursor(self.cursor)

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
    

class RectangleMapTool(QgsMapToolEmitPoint):
    rectangleCreated = pyqtSignal(float, float, float, float)
    
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setStrokeColor(Qt.black)
        self.rubberBand.setWidth(1)
        self.reset()
    
    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
    
    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)
    
    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
#        self.rubberBand.hide()
        self.transformCoordinates()
        self.rectangleCreated.emit(self.startPoint.x(),
                                   self.startPoint.y(),
                                   self.endPoint.x(),
                                   self.endPoint.y())
    
    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
    
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)
    
    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return
    
        point1 = QgsPointXY(startPoint.x(), startPoint.y())
        point2 = QgsPointXY(startPoint.x(), endPoint.y())
        point3 = QgsPointXY(endPoint.x(), endPoint.y())
        point4 = QgsPointXY(endPoint.x(), startPoint.y())
        
        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)# true to update canvas
        self.rubberBand.show()
    
    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None
    
        return QgsRectangle(self.startPoint, self.endPoint)    
    
    
    def transformCoordinates(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None

        # Defining the crs from src and destinysetColor
        crsSrc = self.canvas.mapSettings().destinationCrs()
        crsDest = QgsCoordinateReferenceSystem(4326)
        # Creating a transformer
        coordinateTransformer = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        # Transforming the points
        self.startPoint = coordinateTransformer.transform(self.startPoint)
        self.endPoint = coordinateTransformer.transform(self.endPoint)
        
    
    def deactivate(self):
        super(RectangleMapTool, self).deactivate()
        #QgsMapToolEmitPoint.deactivate(self)