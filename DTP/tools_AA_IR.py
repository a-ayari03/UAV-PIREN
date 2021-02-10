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
from rasterio.plot import plotting_extent
from rasterio.plot import show
from rasterio.plot import show_hist # Useful if you wish to plot all hist and GPS target image
from rasterio.mask import mask
import fiona

def reading_gps_file(filename):
    """ 
    Lit un fichier '.txt' contenant les valeurs UTM des sondes
    output : DataFrame de la position et nom des sondes
    
    """
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
        Raw_sensor = np.array([sensor_Name_File_GPS,sensor_x,sensor_y]).T # Transpose
        # Transformation en DataFrame 
        sensor_coord =pd.DataFrame(Raw_sensor,columns= ["SensorName","x","y"])
    return sensor_coord

def circle_sensor(SensorName,Sensor_coord,r=1):
    
    """
    SensorName : nom du(des) sensor(s) souhaité(s), Sensor_coord : résultat de la fonction reading_gps_file
    r : rayon en metre, 1.00 m par défaut
    Output : 
    list_coord_circle = list des coordonnes des extremites de chaque cercle
    Shape_to_json     = list Proprietes geometriques de chaque cercle
    circle_name       = list de noms des sensors
    
    """
    list_coord_circle = []
    Shape_to_json=[]
    circle_name = []
    
    for SensorName in SensorName :
        sensor_GPS = Sensor_coord.loc[Sensor_coord['SensorName']==str(SensorName)]
        center = Point(sensor_GPS["x"],sensor_GPS["y"]) # point central
        circle = center.buffer(r)
        x_circle,y_circle = circle.exterior.xy #Val de chaque extremitees du cercle
        list_coord_circle.append([np.array(x_circle),np.array(y_circle)])
        
        # Transfo des donnees en Geoseries : 
        #Json -> https://fr.wikipedia.org/wiki/JavaScript_Object_Notation
        # Format qui contient toutes les proprietes + points ext du cercle
        Shape_to_json.append(gpd.GeoSeries([circle]).to_json())
        circle_name.append(sensor_GPS['SensorName'])
        
    return list_coord_circle,Shape_to_json,circle_name
    
def circle_to_shape(list_coord_circle,Shape_to_json):
    """ 
    Input : 
    list_coord_circle = list des coordonnes des extremites de chaque cercle
    Shape_to_json     = list Proprietes geometriques de chaque cercle
    Transormation des points de circle_sensor en shape, utile pour le mask 
    Output : Shape = cercle d'un rayon r autour de sonde(s)
    """
    shapes = []
    for j in range(len(list_coord_circle)):
        with fiona.open(Shape_to_json[j],'r') as image:
            #print(list(image)) # On va chercher à chopper la propriete Geometry
            shapes.append([feature["geometry"] for feature in image])
    print("nombre de shapes",len(shapes))
    return shapes

    
def path_IR(path = './traitement_PIREN/') :
    """
    Recupere les noms des IR dans le dossier path, par defaut = './traitement_PIREN/'
    output : list des chemins d'acces pour chaque fichier '.tif'
    V2 : INUTILISE AU PROFIL DE GET_TIF
    """
    ls_path_tif =[]
    ls_path = os.listdir(path=path)
    for tif in ls_path:
        if tif.find('.tif') > 0 :
            ls_path_tif.append([path+tif])
    return ls_path_tif

def get_tif(filetif,path = './traitement_PIREN/') :
    """
    Recoit les noms des .tifs souhaites ainsi que le dossier d'acces
    
    """
    
    ls_path_tif =[]
    ls_path = os.listdir(path=path)
    path_tif = []
    for tif in ls_path:
        if tif.find('.tif') > 0 :
            ls_path_tif.append([path+tif])
    for FILETIF in filetif :
        for tif_name in ls_path_tif:
            if tif_name[0].find(str(FILETIF)) > 0 :
                path_tif.append(tif_name[0])
    return path_tif, filetif

def get_value_IR(Sensor_coord,IR_src) : 
    """
    Input : Dataframe des positions des sensors , IR choisi
    Obtient la valeur d'une coordonnée dans l'IR correspondante 
    output : numpy.ndarray contenant positions et valeurs 
    """
    len_coord = len(Sensor_coord) 
    value = []
    ls_value = []
    for k in range(0,len_coord) :
        for val in IR_src.sample([(float(Sensor_coord["x"][k]),float(Sensor_coord["y"][k]))]): 
            value.append(val)
        coord_value = np.array([Sensor_coord["x"],Sensor_coord["y"],value],dtype=object)
    ls_value.append(coord_value)
    return ls_value
    
def readingIR(ls_path_tif,filetif) : 
    Piren_IR_ls = []
    Piren_IR_name = []
    mapping_columns = {}
    for path_tif in ls_path_tif :
        IR_src = rio.open(os.path.join(path_tif))
        Piren_IR_array=IR_src.read(1) # Lit la bande 1
        Piren_Limits = plotting_extent(IR_src) # Limites
        Piren_res = IR_src.res # resolution
        Piren_IR_ls.append([Piren_IR_array,Piren_Limits,IR_src])
    Piren_IR_name.append(filetif)
    Piren_IR = pd.DataFrame(np.array([Piren_IR_ls[0][0],Piren_IR_ls[0][1],Piren_IR_ls[0][2]],dtype=object).T,index =
                            ["IR_array","Limits","IR_src"],columns = ['IR_'+filetif[0]])

    return Piren_IR,Piren_IR_ls
    

def IR_mask(ls_IR_src,shapes,list_coord_circle) : 
    ls_out_image = []
    ls_out_transform = []
    for IR_src in ls_IR_src :
        out_image = []
        out_transform = []
        out_meta = IR_src.meta
        for k in range(len(list_coord_circle)) :
            image, transform = rio.mask.mask(IR_src, shapes[k], crop=True, filled=False)
            """
            And update height and width of cropped image with its meta data
            """
            out_meta.update({"driver": "GTiff",
                     "height": image.shape[1],
                     "width": image.shape[2],
                     "transform": transform})
            out_image.append(image)
        ls_out_image.append(out_image)
        ls_out_transform.append(transform)
    return ls_out_image, ls_out_transform
        
    