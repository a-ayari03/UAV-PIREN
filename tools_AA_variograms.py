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

def get_3band(filename) :
    """ 
    Lit 3 bandes et les stacks dans une seule et même matrice
    """
    
    with rio.open(filename) as dataset :
        band_1 = dataset.read(1)
        band_2=dataset.read(2)
        band_3=dataset.read(3)
        band_stack = np.dstack((band_1,band_2,band_3))
    return band_stack
        

def reshape_3band_to_dataframe (ARRAY_2D) :
    print('Original shape',":",ARRAY_2D.shape)
    pixel = ARRAY_2D.reshape((-1,3))
    pixel = pd.DataFrame(np.array(pixel),
                            columns = ["band 1","band 2","band 3"])
    print("pixel shape :",pixel.shape)
    return pixel
    

def set_bound_to_NAN(pixel_raw,HSV = False) :
    """
    Lit un DataFrame 1D d'une image 3 bandes et exclu les valeurs
    (255,255,255) représentant aucune donnée réelle par des NaN
    output : 
    empty_matrix : matrice de la shape initiale à une bande 
    pixel : contient les valeurs 
    pixel_location_1D : contient les indices des des valeurs
    """
    if HSV :
        RGB = get_3band('./traitement_PIREN/vis_piren_phase_1_cropped.tif')
        pixel_raw_vis = reshape_3band_to_dataframe(RGB)
        condition = np.array([pixel_raw_vis["band 1"] == 255,
                              pixel_raw_vis["band 2"] == 255,
                              pixel_raw_vis["band 3"] == 255]).T
    else : 
        condition = np.array([pixel_raw["band 1"] == 255,
                              pixel_raw["band 2"] == 255,
                              pixel_raw["band 3"] == 255]).T
        
    pixel_255_1 = pixel_raw["band 1"].mask(condition.all(axis = 1))
    pixel_255_2 = pixel_raw["band 2"].mask(condition.all(axis = 1))
    pixel_255_3 = pixel_raw["band 3"].mask(condition.all(axis = 1))
    pixel_255 = pd.DataFrame(np.array([pixel_255_1,pixel_255_2,pixel_255_3]).T,columns = ["band 1","band 2","band 3"])
    
    #MASKED WHERE BAND1 BAND2 BAND3 = (255,255,255)
    pixel_255_1 = pixel_raw["band 1"].mask(condition.all(axis = 1))
    pixel_255_2 = pixel_raw["band 2"].mask(condition.all(axis = 1))
    pixel_255_3 = pixel_raw["band 3"].mask(condition.all(axis = 1))
    pixel_255 = pd.DataFrame(np.array([pixel_255_1,pixel_255_2,pixel_255_3]).T,columns = ["band 1","band 2","band 3"])
    
    #Indice location of pixel == NaN // pixel != NaN
    pixel_location = np.nonzero(np.array(pixel_255).reshape(-1,3) >=0)
    pixel_location_NAN = np.nonzero(condition.reshape(-1,3) == True  )
    # indices des valeurs != NAN en 1D
    pixel_location_1D = np.nonzero(np.array(pixel_255["band 1"]).reshape(-1,1) >=0)
    
    # On garde que les valeurs 
    pixel = np.array(pixel_255.dropna(axis = "rows")).reshape(-1,3)
    
    #Pré-allocation d'une matrice de NAN de shape similaire à la taille originale(pour une bande)
    empty_matrix = np.empty((np.array(pixel_255).reshape(-1,3).shape[0],1))
    empty_matrix[:] = np.NAN
    print("empty_matrix shape :",empty_matrix.shape)
    empty_matrix = empty_matrix.astype("float32")
    pixel = pixel.astype('float32')
    
    return empty_matrix,pixel,pixel_location_1D

    
    
def reading_3band(LONGUEUR,filename='./traitement_PIREN/vis_piren_phase_HSV.tif',normalization = True) :
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

        dict_windows = {} # liste des paramètres dans la création d'une window
        dict_windows_param = {} # dict des targets : améliore la lisibilité

        for i,index_target in enumerate(ls_index_target) :
            win = Window.from_slices((index_target[0]-(win_height//2),(index_target[0]+(win_height//2))),
                                     (index_target[1]-(win_width//2),(index_target[1]+(win_width//2)))
                                     )
            win_transform = dataset.window_transform(win)
            all_band = dataset.read([1,2,3],window = win) # en cas de visualisation

            dict_param = {"win" : win,
                            "win_transform" : win_transform,
                           "all_band" : all_band,
                           "SensorName" : sensor_coord["SensorName"][i]}

            dict_windows_param[sensor_coord["SensorName"][i]] = dict_param

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
            if normalization == False :
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
         
            
    return dict_windows, dict_windows_param  

def reading_cluster(LONGUEUR,filename='./traitement_PIREN/vis_piren_phase_HSV.tif', x = None,y = None) :
    """ Lit un fichier .tif à 1 bands et retourne un patch carré de coté LONGUEUR au format csv pour l'execution d'un variogram
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
        if x != None or y != None :
            ls_index_target.append(dataset.index(float(x),float(y)))
        else :
            
            for k in range(len(sensor_coord["SensorName"])) :
                x = sensor_coord["x"][k] 
                y = sensor_coord["y"][k]
                target = dataset.index(float(x),float(y))
                ls_index_target.append(target)

        dict_windows = {} # liste des paramètres dans la création d'une window
        dict_windows_param = {} # dict des targets : améliore la lisibilité

        for i,index_target in enumerate(ls_index_target) :
            win = Window.from_slices((index_target[0]-(win_height//2),(index_target[0]+(win_height//2))),
                                     (index_target[1]-(win_width//2),(index_target[1]+(win_width//2)))
                                     )
            win_transform = dataset.window_transform(win)
            all_band = dataset.read(1,window = win) # en cas de visualisation

            dict_param = {"win" : win,
                            "win_transform" : win_transform,
                           "all_band" : all_band,
                           "SensorName" : sensor_coord["SensorName"][i]}

            dict_windows_param[sensor_coord["SensorName"][i]] = dict_param

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
            x_matrix = []
            y_matrix = []
            # Loop pour obtenir la valeur de chaque pt pour chaque band
            for j in range(len(x)) :
                for l in range(len(y)) :
                    for val in dataset.sample([(x[j],y[l])]): 
                        label = val[0]
                        band_1.append(label)
                        x_matrix.append(x[j]) # permet de répeter le terme 
                        y_matrix.append(y[l])
                        mapping = ['x','y','label']
            DATA_WINDOW = pd.DataFrame(np.array([x_matrix,
                                                 y_matrix,
                                                 band_1],dtype = object).T,
                                       columns=mapping)
            
            DATA_WINDOW['SensorName'] = sensor_coord["SensorName"][i]
            
            dict_windows[sensor_coord["SensorName"][i]] = DATA_WINDOW
         
            
    return dict_windows, dict_windows_param 


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
        