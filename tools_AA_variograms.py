#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 18:32:01 2020

@author: el
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import geopandas as gpd
import rasterio as rio
from rasterio.plot import show
from rasterio.plot import show_hist # Useful if you wish to plot all hist and GPS target image
from rasterio.mask import mask
from rasterio.windows import Window
from tools_AA_IR import reading_gps_file,get_tif,circle_sensor,circle_to_shape

def reading_3band(LONGUEUR,filename='./traitement_PIREN/vis_piren_phase_HSV.tif') :
    """ Lit un fichier .tif à 3 bands et retourne un patch carré de coté LONGUEUR au format csv pour l'execution d'un variogram
    """
    #filename = './traitement_PIREN/vis_piren_phase_HSV.tif'
    #LONGUEUR = 10
    filename_Sensor_txt = "./traitement_PIREN/sondes_gps_UTM31N_phase1.txt"
    sensor_coord = reading_gps_file(filename_Sensor_txt)
    with rio.open(filename) as dataset :
        #Value par défaut
        #win_height = 6303
        #win_width = 3421

        ls_index_target = [] # liste des valeurs indexées dans l'image
        win_height = round(LONGUEUR / dataset.res[0])
        win_width  = round(LONGUEUR / dataset.res[1])
        print("Taille de la fenetre :",win_height,"x",win_width)

        # Loop pour recuperer les coordonnées UTM et convertir en indice 
        for k in range(len(sensor_coord["SensorName"])) :
            x = sensor_coord["x"][k] 
            y = sensor_coord["y"][k]
            target = dataset.index(float(x),float(y))
            ls_index_target.append(target)

        ls_windows_param = [] # liste des paramètres dans la création d'une window
        dict_windows = {} # dict des targets : améliore la lisibilité

        for i,index_target in enumerate(ls_index_target) :
            win = Window(index_target[0],index_target[1],win_height,win_width)
            win_transform = dataset.window_transform(win)
            all_band = dataset.read([1,2,3],window = win) # en cas de visualisation

            dict_windows_param = {"win" : win,
                            "win_transform" : win_transform,
                           "all_band" : all_band,
                           "SensorName" : sensor_coord["SensorName"][i]}

            ls_windows_param.append(dict_windows_param)

            # Vecteurs linéaires avec valeurs uniforméments crées
            x_start = win_transform[2]
            x_res   = win_transform[0]
            x_end   = x_start+(float(x_res)*win.width)

            y_end   = win_transform[5]
            y_res   = win_transform[4]
            y_start = y_end + (float(y_res)*win.height)

            #print("x_end =",x_end)
            #print("y_start =",y_start)

            x = np.linspace(x_start,x_end,num = win.width)
            y = np.linspace(y_start,y_end,num = win.height)

            band_1 = []
            band_2 = []
            band_3 = []
            band_RGB = []
            band_greeness =[]
            x_matrix = []
            y_matrix = []
            # Loop pour obtenir la valeur de chaque pt pour chaque band
            if filename.find('normalized')<0 :
                for j in range(len(x)) :
                    for l in range(len(y)) :
                        for val in dataset.sample([(x[j],y[l])]): 
                            R = val[0]
                            G = val[1]
                            B = val[2]
                            band_1.append(R)
                            band_2.append(G)
                            band_3.append(B)
                            x_matrix.append(x[j]) # permet de répeter le terme 
                            y_matrix.append(y[l])
                            mapping = ['x','y','band 1','band 2','band 3']
                DATA_WINDOW = pd.DataFrame(np.array([x_matrix,
                                                     y_matrix,
                                                     band_1,
                                                     band_2,
                                                     band_3],dtype = object).T,
                                           columns=mapping)
                        
            else :
                for j in range(len(x)) :
                    for l in range(len(y)) :
                        for val in dataset.sample([(x[j],y[l])]): 
                            R = val[0]
                            G = val[1]
                            B = val[2]
                            band_1.append(R)
                            band_2.append(G)
                            band_3.append(B)
                            RGB = np.sqrt(R**2 + G**2 + B**2)
                            Greeness = G/(R+G+B)
                            band_RGB.append(RGB)
                            band_greeness.append(Greeness)
                            x_matrix.append(x[j]) # permet de répeter le terme 
                            y_matrix.append(y[l])
                            
                mapping = ['x','y','band 1',
                           'band 2','band 3',
                           'band RGB','band Greensess']
                print(len(band_greeness))
                DATA_WINDOW = pd.DataFrame(np.array([x_matrix,
                                                     y_matrix,
                                                     band_1,
                                                     band_2,
                                                     band_3,
                                                    band_RGB,
                                                     band_greeness],
                                                    dtype = object).T,
                                           columns=mapping)
   
            DATA_WINDOW['SensorName'] = sensor_coord["SensorName"][i]
            
            dict_windows[sensor_coord["SensorName"][i]] = DATA_WINDOW
         
            
    return dict_windows, ls_windows_param  



def vario_all_target(dict_windows,n_lags) : 
    dict_variogram = {}
    for target in dict_windows :
        print(target)
        values_1 = dict_windows[target]["band 1"]
        values_2 = dict_windows[target]["band 2"]
        values_3 = dict_windows[target]["band 3"]

        V1 = Variogram(coords,values_1,
                       model = "spherical",n_lags=nb_lag)
        V2 = Variogram(coords,values_2,
                  model = "spherical",n_lags=nb_lag)

        V3 = Variogram(coords,values_3,
                  model = "spherical",n_lags=nb_lag )
        dict_variogram[target] = [V1,V2,V3]
    return dict_variogram
        