#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 00:49:36 2018

@author: nilsnolde
"""

from OSMtools import convert

def reverse_geocode(client, point_in):
    params = dict()
    params['point.lat'] = point_in.y()
    params['point.lon'] = point_in.x()
    
    try:
        response = client.request('/geocode/reverse', params)['features'][0]
    except:
        raise #ValueError("Your input coordinates are invalid for geocoding.")
    
    response_dict = dict()
    
    x, y = response['geometry'].get('coordinates',None)
    response_dict['Lon'] = x
    response_dict['Lat'] = y
    response_dict['COUNTRY'] = response['properties'].get('country', None)
    response_dict['STATE'] = response['properties'].get('state', None)
    response_dict['CITY'] = response['properties'].get('county', None)
    response_dict['POSTALCODE'] = response['properties'].get('postal_code', None)
    response_dict['STREET'] = response['properties'].get('street', None)
    response_dict['NUMBER'] = response['properties'].get('house_number', None)
                       
    return response_dict