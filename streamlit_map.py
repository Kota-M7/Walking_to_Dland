import streamlit as st
import time
import pandas as pd
import sqlite3 
import hashlib
import datetime
import plotly.graph_objects as go
import numpy as np
import math
import folium
from streamlit_folium import folium_static

kisarazu_lat=35.382062022979206
kisarazu_lon=139.92613949878296
r_earth=6371#地球の半径km（wikipedia）

td_lat=35.63044153732999
td_lon=139.88395943810684

dt_now = datetime.datetime.now()
dt_today = datetime.date.today()

conn = sqlite3.connect('database.db')
c = conn.cursor()
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

def create_user():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

def add_user(username,password):    
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def main():
    st.title("🐾お散歩記録アプリ🐾")
    st.write(str(dt_now.year)+'年'+str(dt_now.month)+'月'+str(dt_now.day)+'日')
    menu = ["ログイン"]
    choice = st.sidebar.selectbox("メニュー",menu)

    if choice == "ログイン":
        username = st.sidebar.text_input("ユーザー名を入力してください")
        password = st.sidebar.text_input("パスワードを入力してください",type='password')

        if st.sidebar.checkbox("ログイン"):
            create_user()
            hashed_pswd = make_hashes(password)
            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:
                st.success("【認証成功】{}さんがログインしました".format(username))
                time.sleep(1)
                df_length = pd.read_csv('pandas_length_data.csv', index_col=0)
                print(df_length.iloc[-1,4])

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


                data = {
                    'lat': df_length.iloc[:,4] + kisarazu_lat,
                    'lon':B + kisarazu_lon,
                }
                map_data = pd.DataFrame(data)
    
                ########################################
                # サンプル用の緯度経度データを作成する
                sales_office = pd.DataFrame(
                    data=[[kisarazu_lat,kisarazu_lon]],
                    index=["木更津駅"],
                    columns=["x","y"]
                )

                # データを地図に渡す関数を作成する
                def AreaMarker(df,m):
                    for index, r in df.iterrows(): 

                        # ピンをおく
                        folium.Marker(
                            location=[r.x, r.y],
                            popup=index,
                        ).add_to(m)

                        # 円を重ねる
                        folium.Circle(
                            radius=sum*1000,
                            location=[r.x, r.y],
                            popup=index,
                            color="red",
                            fill=True,
                            fill_opacity=0.01
                        ).add_to(m)
                        # 円を重ねる
                        folium.Circle(
                            radius=rad*1000,
                            location=[r.x, r.y],
                            popup=index,
                            color="gray",
                            fill=True,
                            fill_opacity=0.01
                        ).add_to(m)


                # ------------------------画面作成------------------------

                rad = st.slider('木更津駅を中心とした円の半径（km）',value=5,min_value=1, max_value=60) # スライダーをつける
                #st.subheader("各拠点からの距離{:,}km".format(rad)) # 半径の距離を表示
                m = folium.Map(location=[kisarazu_lat,kisarazu_lon], zoom_start=10) # 地図の初期設定
                AreaMarker(sales_office,m) # データを地図渡す
                folium.Marker(location=[td_lat, td_lon],popup="ディズニー",icon=folium.Icon(icon="bell", icon_color='#ffff00', color="pink")).add_to(m)
                folium.Marker(location=[35.464715647378526, 139.87409742577145],popup="海ほたる",icon=folium.Icon(color="lightblue")).add_to(m)
                folium.Marker(location=[35.442944594677336, 139.64568118159403],popup="横浜中華街",icon=folium.Icon(icon="cutlery", icon_color='white', color="lightgreen")).add_to(m)
                folium.Marker(location=[35.689707215357096, 139.69209075091902],popup="都庁展望台",icon=folium.Icon(icon="glyphicon-star", icon_color='yellow', color="darkblue")).add_to(m)
                folium.Marker(location=[35.67882004106522, 139.76264298344913],popup="エシレ",icon=folium.Icon(icon="cutlery", icon_color='white', color="purple")).add_to(m)
                folium.Marker(location=[35.77713744579061, 139.79034243359916],popup="西新井",icon=folium.Icon(color="lightblue")).add_to(m)
                folium.Marker(location=[35.51055270271422, 140.10123484620277],popup="五井JINS",icon=folium.Icon(icon="glyphicon-eye-open", icon_color='white', color="pink")).add_to(m)
                folium.Marker(location=[35.71628267035655, 139.7959246345603],popup="浅草寺",icon=folium.Icon(color="orange")).add_to(m)
                folium.Marker(location=[35.251674388714974, 139.0456591253867],popup="箱根強羅公園",icon=folium.Icon(color="beige")).add_to(m)
                folium.Marker(location=[36.31156087377431, 140.57765846517333],popup="大洗かねふく",icon=folium.Icon(icon="cutlery", icon_color='white', color="lightblue")).add_to(m)
                folium.Marker(location=[35.1162635749556, 140.1204945587839],popup="鴨川シーワールド",icon=folium.Icon(icon="glyphicon-camera", icon_color='black', color="lightblue")).add_to(m)
                folium.Marker(location=[35.42780315468488, 139.9153354127578],popup="コストコ",icon=folium.Icon(color="beige")).add_to(m)
                folium.Marker(location=[35.31331971078233, 139.78374879621708],popup="富津岬",icon=folium.Icon(color="lightblue")).add_to(m)
                folium.Marker(location=[13.44531491556728, 144.75992857019287],popup="グアム",icon=folium.Icon(color="pink")).add_to(m)
                folium.Marker(location=[df_length.iloc[-1,4] + kisarazu_lat, kisarazu_lon],popup="現在地",icon=folium.Icon(color="red")).add_to(m)
    
                st.subheader("どこまで歩いた？")
                folium_static(m) # 地図情報を表示
    
                # 地図に散布図を描く
                st.subheader("これまでの記録")
                st.map(map_data)

            else:
                st.warning("ユーザー名かパスワードが間違っています")

if __name__ == '__main__':
    main()
