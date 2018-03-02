#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 10:39:11 2018

@author: nilsnolde
"""

from itertools import product

from PyQt5.QtWidgets import (QComboBox,
                             QLabel,
                             QCheckBox
                             )

from PyQt5.QtCore import QVariant

from qgis.core import (QgsVectorLayer,
                       QgsField, 
                       QgsPointXY,
                       QgsGeometry,
                       QgsFeature,
                       QgsProject
                       )

from . import convert, geocode, auxiliary, pointtool

class places:
    """
    Performs requests to the ORS places API.
    """
    def __init__(self, dlg, client, iface):
        """
        :param dlg: Main OSMtools dialog window.
        :type dlg: QDialog
        
        :param client: Client to ORS API.
        :type client: OSMtools.client.Client()
        
        :param iface: A QGIS interface instance.
        :type iface: QgisInterface
        """
        self.dlg = dlg
        self.client = client
        self.iface = iface
        
        self.url = '/places'        
        self.mapTool = pointtool.RectangleMapTool(self.iface.mapCanvas())
        
#        self.params = {'profile': self.route_mode,
#                    'preference': self.route_pref,
#                    'geometry': 'true',
#                    'geometry_format': 'geojson',
#                    'instructions': 'false'
#                    }
        
    def places_calc(self):
        """
        Performs requests to the ORS places API.
        """
        