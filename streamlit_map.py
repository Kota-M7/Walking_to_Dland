import streamlit as st
import time
import pandas as pd
import sqlite3 
import hashlib
import datetime
import plotly.graph_objects as go
import numpy as np
import math

dt_now = datetime.datetime.now()
dt_today = datetime.date.today()




kisarazu_lat=35.382062022979206
kisarazu_lon=139.92613949878296
r_earth=6371#地球の半径km（wikipedia）


def main():
    st.title("🐾お散歩記録アプリ🐾")
    st.write(str(dt_now.year)+'年'+str(dt_now.month)+'月'+str(dt_now.day)+'日')
    df_length = pd.read_csv('pandas_length_data.csv', index_col=0)

    hosuu=st.text_input('歩数(歩)　例：1000')
    length=float(hosuu)*0.00072
    x=180*float(length)/(math.pi*r_earth)

    if df_length['date'][-1:].values[0] == str(dt_today):
        df_length=df_length[:-1]
        sum=length+df_length['total_length'][-1:].values[0]
        sum_lat=180*float(sum)/(math.pi*r_earth)

        df_length=df_length.append({'date': str(dt_today),'hosuu': float(hosuu),'length': float(length),'total_length': sum,'total_lat': sum_lat}, ignore_index=True)

    else:
        sum=length+df_length['total_length'][-1:].values[0]
        sum_lat=180*float(sum)/(math.pi*r_earth)
        df_length=df_length.append({'date': str(dt_today),'hosuu': float(hosuu),'length': float(length),'total_length': sum,'total_lat': sum_lat}, ignore_index=True)

    if sum_lat+kisarazu_lat>=35.63168740503107:
        st.write("ディズニーランドに到達！🐭")
    
    fig_length = go.Figure()
    fig_length.add_trace(go.Scatter(x=df_length['date'],
								y=df_length['length'],
											 mode='lines',
											 name='距離km'))
    
    fig_length.add_trace(go.Scatter(x=df_length['date'],
								y=df_length['total_length'],
											 mode='lines',
											 name='総距離km'))
    
    df_length.to_csv('pandas_length_data.csv')
    st.write(fig_length)
    A=np.array([0.0]* df_length.shape[0])
    B=np.array([0.0]* df_length.shape[0])

    #for i in range(0,df_length.shape[0],1):
    #    A[i]=df_length['total_lat'](i)

    # 東京のランダムな経度・緯度を生成する
    data = {
        #'lat': np.random.randn(10) / 100 + 35.68,
        #'lon': np.random.randn(10) / 100 + 139.75,
        #'lat': np.array([0,-x]) + kisarazu_lat,
        #'lon':np.array([0,0]) + kisarazu_lon,
        'lat': df_length.iloc[:,4] + kisarazu_lat,
        'lon':B + kisarazu_lon,
    }
    map_data = pd.DataFrame(data)
    # 地図に散布図を描く
    st.map(map_data)


if __name__ == '__main__':
    main()
