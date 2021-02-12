# -*- coding: utf-8 -*-
"""
Created on Thu Feb  10 10:19:42 2021

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
from skimage.color import rgb2hsv
from tools_AA_IR import reading_gps_file,get_tif,circle_sensor,circle_to_shape

    
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
    
    
def readingVIS(ls_path_tif,filetif) : 
    Piren_VIS_ls = []
    Piren_VIS_name = []
    mapping_columns = {}
    for path_tif in ls_path_tif :
        VIS_src = rio.open(os.path.join(path_tif))
        Piren_VIS_array=VIS_src.read() # Lit les bandes
        Piren_Limits = plotting_extent(VIS_src) # Limites
        Piren_res = VIS_src.res # resolution
        Piren_transform = VIS_src.transform
        Piren_VIS_ls.append([Piren_VIS_array,Piren_Limits,VIS_src,Piren_transform])

    Piren_VIS_name.append(filetif)
    Piren_VIS = pd.DataFrame(np.array([Piren_VIS_ls[0][0],Piren_VIS_ls[0][1],Piren_VIS_ls[0][2],Piren_VIS_ls[0][3]],dtype=object).T,index =
                            ["VIS_array","Limits","VIS_src","VIS_transform"],columns = ['Phase_1'])

    return Piren_VIS,Piren_VIS_ls



def readingVIS_norm(ls_path_tif,filetif) :
    #print("ls_path_tif :" , ls_path_tif)
    Piren_VIS_ls = []
    Piren_VIS_name = []
    mapping_columns = {}
    for path_tif in ls_path_tif :
        VIS_src = rio.open(os.path.join(path_tif))
        #print("VIS_src :",VIS_src)
        Piren_VIS_array =  VIS_src.read()
        Piren_Limits = plotting_extent(VIS_src) # Limites
        Piren_res = VIS_src.res # resolution
        Piren_transform = VIS_src.transform
        Piren_VIS_ls.append([Piren_VIS_array,Piren_Limits,VIS_src,Piren_transform])
        Piren_VIS_name.append(filetif)        
    Piren_VIS = pd.DataFrame(np.array([Piren_VIS_ls[0][0],Piren_VIS_ls[0][1],Piren_VIS_ls[0][2],Piren_VIS_ls[0][3]],dtype=object).T,index =
                            ["VIS_array","Limits","VIS_src","VIS_transform"],columns = ['Phase_1'])

    #print("Piren_VIS.loc['VIS_src'][0]:",Piren_VIS.loc["VIS_src"][0])
    return Piren_VIS,Piren_VIS_ls

def VIS_mask(ls_VIS_src,shapes,list_coord_circle) : 
    ls_out_image = []
    ls_out_transform = []
    for VIS_src in ls_VIS_src :
        out_image = []
        out_transform = []
        out_meta = VIS_src.meta
        for k in range(len(list_coord_circle)) :
            image, transform = rio.mask.mask(VIS_src, shapes[k], crop=True, filled=False)
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
      
    
def plottingtemp_single_label_IR(Raw,fig,ax1,label,step):
    coloration=plt.cm.Set1(np.linspace(0,1,10))
    random_color = np.random.randint(10)
    dict_label = {'T1' :'T1-0.50','T2' :'T2-0.35','T3' :'T3-0.20','T4' :'T1-0.05'}
    for name in Raw["SensorName"] :
        ss = name
        
    label_name = ss+str(dict_label[str(label)])
    ax1.plot(Raw['Time'], Raw[str(label)], color=coloration[random_color,:],label=label_name)
    plt.xticks(Raw.Time[::step])
    plt.title(ss)
    ax1.legend()
    ax1.grid()
    fig.autofmt_xdate()
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temp [C]')  

    
def get_requested_tif(filetif,path = './traitement_PIREN/') :
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
            if tif_name[0].find(str(FILETIF)) == 0 :
                path_tif.append(tif_name[0])
    print(ls_path_tif)
    return path_tif, filetif


def requested_VIS_AOI (filetif,request_sensor) :
    
    ls_path_tif,filetif = get_tif(filetif)
    print(ls_path_tif)
    Piren_VIS,Piren_VIS_ls= readingVIS_norm(ls_path_tif,filetif)

    # Ouverture et recupération des positions des sondes
    filename_Sensor_txt = "./traitement_PIREN/sondes_gps_UTM31N_phase1.txt"
    Sensor_coord = reading_gps_file(filename_Sensor_txt)
    Sensor_coord # Contient les coord de toutes les sondes
    ## creation d'un rayon de taille r autour des sensors
    ls_sensor = Sensor_coord["SensorName"] # : toutes les sondes
    ls_coord_circle,Shape_to_json,circle_name = circle_sensor(ls_sensor,Sensor_coord)

    #Creat a shape in GeoJSON format in order to be read with rio and 
    #serve as mask to crop selected area in the shape

    shapes,shapes_names = circle_to_shape(ls_coord_circle,Shape_to_json,circle_name)

    requested_names  =  []
    requested_shapes =  []
    requested_ls_coord_circle = []
    for i,names in enumerate(shapes_names) :
        for k in range(len(request_sensor)) :  
            if names == request_sensor[k] :
                requested_names.append(names)
                requested_shapes.append(shapes[i])
                requested_ls_coord_circle.append(ls_coord_circle[i])


    ## Creation de mask pour UNE IMAGE
    ls_mask_image, ls_out_transform= VIS_mask(Piren_VIS.loc["VIS_src"],shapes,ls_coord_circle)
    return requested_names, requested_shapes, ls_mask_image, ls_out_transform,Piren_VIS

def norm_tif(filetif) : 
    
    ls_path_tif,filetif = get_tif(filetif) 
    #print(ls_path_tif)
    
    request = './traitement_PIREN/vis_piren_phase_normalized.tif'
    path_VIS = './traitement_PIREN/vis_piren_phase1_ortho_UTM31N.tif'
    k = 0
    while ls_path_tif[k].find(request) != 0 and k<len(ls_path_tif)-1 :
        k+=1
    path_request = ls_path_tif[k]
    print(path_request)
    if path_request != request :
        
        with rio.open(os.path.join(path_VIS)) as VIS_src :
            print("VIS_src :",VIS_src)

            Red_N,Green_N,Blue_N = norm(VIS_src)
            profile = {
                "driver": "GTiff",
                "count": 3,
                "height": VIS_src.shape[0],
                "width": VIS_src.shape[1],
                'dtype': 'float32',
                'transform': VIS_src.transform,
                "meta" : VIS_src.meta ,
                "bounds": VIS_src.bounds ,
                "crs": VIS_src.crs ,
                "res": VIS_src.res }

            with rio.open(
                './traitement_PIREN/vis_piren_phase_normalized.tif', 'w',
                **profile) as dst: # count : nombre de band
                for k, arr in [(1, Red_N), (2, Green_N), (3, Blue_N)]:
                    dst.write(arr.astype(rio.float32), indexes=k)

 
    filetif_norm = ["vis_piren_phase_normalized"]
    return filetif_norm,request
            
def norm(VIS_src) :
    
    Red=VIS_src.read(1)
    Green=VIS_src.read(2)
    Blue=VIS_src.read(3)
    Red=Red.astype('f4')
    Green=Green.astype('f4')
    Blue=Blue.astype('f4')
    RGB= np.dstack((Red, Green, Blue)) # On refait un pseudo RGB
    RGB=RGB.astype('float32') # Je veut juste etre sur que c'est du float
    Red_N=Red/np.sqrt(Red**2 + Green**2 + Blue**2);
    Green_N=Green/np.sqrt(Red**2 + Green**2 + Blue**2);
    Blue_N=Blue/np.sqrt(Red**2 + Green**2 + Blue**2);
    
    return Red_N,Green_N,Blue_N

def hsv_tif(filetif) : 
    
    ls_path_tif,filetif = get_tif(filetif) 
    #print(ls_path_tif)
    
    request = './traitement_PIREN/vis_piren_phase_HSV.tif'
    path_VIS = './traitement_PIREN/vis_piren_phase1_ortho_UTM31N.tif'
    k = 0
    while ls_path_tif[k].find(request) != 0 and k<len(ls_path_tif)-1 :
        k+=1
    path_request = ls_path_tif[k]
    print(path_request)
    if path_request != request :
        
        with rio.open(os.path.join(path_VIS)) as VIS_src :
            print("VIS_src :",VIS_src)

            Red_N,Green_N,Blue_N = norm(VIS_src)
            HSV_tif = hsv(Red_N,Green_N,Blue_N)
            profile = {
                "driver": "GTiff",
                "count": 3,
                "height": VIS_src.shape[0],
                "width": VIS_src.shape[1],
                'dtype': 'float32',
                'transform': VIS_src.transform,
                "meta" : VIS_src.meta ,
                "bounds": VIS_src.bounds ,
                "crs": VIS_src.crs ,
                "res": VIS_src.res }

            with rio.open(
                './traitement_PIREN/vis_piren_phase_HSV.tif', 'w',
                **profile) as dst: # count : nombre de band
                for k, arr in [(1, HSV_tif[:, :, 0]), 
                               (2, HSV_tif[:, :, 1]), (3,HSV_tif [:, :, 2])]:
                    dst.write(arr.astype(rio.float32), indexes=k)

 
    filetif_norm = ["vis_piren_phase_HSV"]
    return filetif_norm,request

def hsv(Red_N,Green_N,Blue_N) :
    
    RGB_N = np.dstack((Red_N,Green_N,Blue_N))
    HSV_tif = rgb2hsv(RGB_N)
    
    return HSV_tif
    
    
    
    
    