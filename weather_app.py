import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
import matplotlib.pyplot as plt

st.title("🌤️ 完整版 Open-Meteo 互动天气应用")

# 1. 创建地图，默认中心在首尔
m = folium.Map(location=[37.5665, 126.9780], zoom_start=6)
st.write("点击地图选择位置查看天气信息")
map_data = st_folium(m, width=700, height=500)

if map_data and map_data['last_clicked']:
    lat = map_data['last_clicked']['lat']
    lon = map_data['last_clicked']['lng']
    st.write(f"选择位置：纬度 {lat:.4f}, 经度 {lon:.4f}")

    # 2. 调用 Open-Meteo API 获取当前天气和未来 7 天预报
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&"
        f"hourly=temperature_2m,precipitation,winddirection_10m,windspeed_10m&"
        f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    )
    response = requests.get(url)
    data = response.json()

    # 3. 当前天气
    if "current_weather" in data:
        weather = data["current_weather"]
        st.subheader("当前天气")
        st.write(f"温度：{weather['temperature']}°C")
        st.write(f"风速：{weather['windspeed']} km/h")
        st.write(f"风向：{weather['winddirection']}°")
        st.write(f"天气代码：{weather['weathercode']}")
    else:
        st.error("无法获取当前天气数据")

    # 4. 未来 7 天预报
    if "daily" in data:
        daily = data["daily"]
        df_daily = pd.DataFrame({
            "日期": daily["time"],
            "最高温度": daily["temperature_2m_max"],
            "最低温度": daily["temperature_2m_min"],
            "降雨量": daily["precipitation_sum"]
        })
        st.subheader("未来 7 天预报")
        st.dataframe(df_daily)

        # 温度折线图
        plt.figure(figsize=(8,3))
        plt.plot(df_daily["日期"], df_daily["最高温度"], marker='o', label="最高温度")
        plt.plot(df_daily["日期"], df_daily["最低温度"], marker='o', label="最低温度")
        plt.title("未来 7 天温度变化")
        plt.xlabel("日期")
        plt.ylabel("温度 (°C)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    # 5. 未来 24 小时温度趋势图
    if "hourly" in data:
        hourly = data["hourly"]
        df_hourly = pd.DataFrame({
            "时间": hourly["time"],
            "温度": hourly["temperature_2m"],
            "降雨": hourly["precipitation"],
            "风速": hourly["windspeed_10m"],
            "风向": hourly["winddirection_10m"]
        })
        st.subheader("未来 24 小时温度趋势")
        df_24h = df_hourly.head(24)
        plt.figure(figsize=(8,3))
        plt.plot(pd.to_datetime(df_24h["时间"]), df_24h["温度"], marker='o', color='orange')
        plt.title("未来 24 小时温度变化")
        plt.xlabel("时间")
        plt.ylabel("温度 (°C)")
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(plt)
