import streamlit as st
import requests
from geopy.geocoders import Nominatim

st.title("Open-Meteo Interactive Weather Dashboard 🌤️")

# 1. 用户输入城市
city = st.text_input("请输入城市名称：", "Seoul")

if city:
    # 2. 获取城市经纬度
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city)

    if location:
        lat = location.latitude
        lon = location.longitude
        st.write(f"城市：{city}")
        st.write(f"经度：{lon:.4f}, 纬度：{lat:.4f}")

        # 3. 调用 Open-Meteo API 获取天气
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url)
        data = response.json()

        if "current_weather" in data:
            weather = data["current_weather"]
            st.subheader("当前天气信息")
            st.write(f"温度：{weather['temperature']}°C")
            st.write(f"风速：{weather['windspeed']} km/h")
            st.write(f"风向：{weather['winddirection']}°")
            st.write(f"天气代码：{weather['weathercode']}")
        else:
            st.error("无法获取天气数据")
    else:
        st.error("找不到该城市，请检查拼写")
