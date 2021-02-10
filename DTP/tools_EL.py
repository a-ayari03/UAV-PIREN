#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 18:32:01 2020

@author: el
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def readingtemp(filename):
    Raw=pd.DataFrame()
    Raw=pd.read_csv(filename,skiprows=1)#,names=['Num','Time','T1','T2','T3'])
    Raw.drop(Raw.columns[[6,7,8]],axis=1,inplace=True)
    mapping={Raw.columns[0]:'Num',Raw.columns[1]: 'Time', Raw.columns[2]: 'T1',Raw.columns[3]: 'T2',Raw.columns[4]: 'T3',Raw.columns[5]: 'T4'}
    Raw = Raw.rename(columns=mapping)
    fin=filename.find('.csv')
    debut=filename.find('/',3)
    Raw['SensorName']=filename[debut+1:fin]#2bupdated later
    Raw['Time'] = pd.to_datetime(Raw['Time'])
    return Raw




def plottingtemp(Raw,fig,ax1,step):
    coloration=plt.cm.viridis(np.linspace(0,1,4))
    ax1.plot(Raw['Time'], Raw['T1'], color=coloration[0,:],label='T1-0.50')
    ax1.plot(Raw['Time'], Raw['T2'], color=coloration[1,:],label='T2-0.35')
    ax1.plot(Raw['Time'], Raw['T3'], color=coloration[2,:],label='T3-0.20')
    ax1.plot(Raw['Time'], Raw['T4'], color=coloration[3,:],label='T4-0.05')
    plt.xticks(Raw.Time[::step])
    plt.title(Raw.SensorName[0])
    ax1.legend()
    ax1.grid()
    fig.autofmt_xdate()
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temp [C]')
