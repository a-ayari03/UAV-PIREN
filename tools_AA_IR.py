# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 00:25:42 2021

@author: Alexandre
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import csv
from shapely.geometry.point import Point
import geopandas as gpd
import rasterio as rio

def reading_gps_file(filename):
    sensor_Name_File_GPS=[]
    sensor_x=[]
    sensor_y=[]
    with open(filename) as File_GPS:
        csvReader=csv.reader(File_GPS, delimiter='\t')
        for row in csvReader:
            sensor_Name_File_GPS.append(row[0]) ## colonne nom du fichier
            # str list to float list, for plot option
            sensor_x.append(float(row[1])) # colonne coordonnees x 
            sensor_y.append(float(row[2])) # colonne coordonnees y
        Raw_sensor = np.array([sensor_Name_File_GPS,sensor_x,sensor_y]).T
        sensor_coord =pd.DataFrame(Raw_sensor,columns= ["SensorName","x","y"])
    return sensor_coord

def circle_sensor(SensorName,Sensor_coord,r=1):
    # SensorName : nom du sensor souhaité, Sensor_coord : résultat de reading_gps_file
    #r : rayon en metre, 1m par défaut
    list_coord_circle = []
    Shape_to_json=[]
    circle_name = []
    for SensorName in Sensor_coord['SensorName'] :
        sensor_GPS = Sensor_coord.loc[Sensor_coord['SensorName']==str(SensorName)]
        center = Point(sensor_GPS["x"],sensor_GPS["y"])
        circle = center.buffer(r)
        #Val de chaque extremitees du cercle
        x_circle,y_circle = circle.exterior.xy
        list_coord_circle.append([np.array(x_circle),np.array(y_circle)])
        # Transfo des donnees en Geoseries : 
        #Json -> https://fr.wikipedia.org/wiki/JavaScript_Object_Notation
        # Format qui contient toutes les proprietes + points ext du cercle
        Shape_to_json.append(gpd.GeoSeries([circle]).to_json())
        circle_name.append(sensor_GPS['SensorName'])
    return list_coord_circle,Shape_to_json,circle_name
    
    
def path_IR(path = './traitement_PIREN/') :
   #Recupere les noms des IR dans le dossier path, par defaut = './traitement_PIREN/'
    ls_path_tif =[]
    ls_path = os.listdir(path=path)
    for tif in ls_path:
        if tif.find('.tif') > 0 :
            ls_path_tif.append([path+tif])
    return ls_path_tif

def get_tif(filetif,ls_path_tif) :
    for tif_name in ls_path_tif:
        if tif_name[0].find(str(filetif)) > 0 :
            path_tif = tif_name[0]
            break
    return path_tif

def get_value_IR(Sensor_coord,IR_src) : 
    len_coord = len(Sensor_coord) 
    value = []
    for k in range(0,len_coord) :
        for val in IR_src.sample([(float(Sensor_coord["x"][k]),float(Sensor_coord["y"][k]))]): 
            value.append(val)
        coord_value = np.array([Sensor_coord["x"],Sensor_coord["y"],value])
    return coord_value
    
    
    
    
    