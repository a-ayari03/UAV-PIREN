# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 17:25:06 2021

@author: Alexandre
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def readingtemp_AA(filename):
    Raw=pd.DataFrame()
    Raw=pd.read_csv(filename,skiprows=1)#,names=['Num','Time','T1','T2','T3'])
    Raw.drop(Raw.columns[[6,7,8]],axis=1,inplace=True)
    mapping={Raw.columns[0]:'Num',Raw.columns[1]: 'Time', Raw.columns[2]: 'T1',Raw.columns[3]: 'T2',Raw.columns[4]: 'T3',Raw.columns[5]: 'T4'}
    Raw = Raw.rename(columns=mapping)
    fin=filename.find('.csv')
    debut=filename.find('/Data/S')
    Raw['SensorName']=filename[debut+1:fin]#2bupdated later
    Raw['Time'] = pd.to_datetime(Raw['Time'])
    return Raw

def slice_raw(Raw,date_1,date_2):
    ### Recup les donnees entre deux dates precises
    ### 'dd/mm/yyyy hh:mm'
    date_1 = pd.to_datetime(date_1)
    date_2 = pd.to_datetime(date_2)
    slice_raw = Raw.loc[(Raw['Time']>=date_1) & (Raw['Time']<=date_2) ,:]
    return slice_raw


def path_sonde(path = './Data/') :
    ### Recupere les noms des sondes dans le dossier path, par defaut = './Data/'
    ls_path_sonde = []
    ls_path = os.listdir(path=path)
    for sonde in ls_path:
        ls_path_sonde.append([path+sonde])
    return ls_path_sonde


def name_sonde(ls_path_sonde,NAME) :
    for dir_sonde in ls_path_sonde:
        debut      = dir_sonde[0].index('/Data/S')
        fin        = dir_sonde[0].index('.csv')
        NAME.append(dir_sonde[0][debut+6:fin])
    return NAME


def plottingtemp_single_label(Raw,fig,ax1,label,step):
    coloration=plt.cm.Set1(np.linspace(0,1,10))
    random_color = np.random.randint(10)
    dict_label = {'T1' :'T1-0.50','T2' :'T2-0.35','T3' :'T3-0.20','T4' :'T1-0.05'}
    label_name = Raw.SensorName[0]+str(dict_label[str(label)])
    ax1.plot(Raw['Time'], Raw[str(label)], color=coloration[random_color,:],label=label_name)
    plt.xticks(Raw.Time[::step])
    plt.title(Raw.SensorName[0])
    ax1.legend()
    ax1.grid()
    fig.autofmt_xdate()
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temp [C]')
