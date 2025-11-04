import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
import matplotlib.pyplot as plt

# ====== PAGE CONFIG ======
st.set_page_config(page_title="Open-Meteo Interactive Weather Dashboard", page_icon="🌤️")

# ====== PAGE INTRODUCTION ======
st.title("🌤️ Open-Meteo Interactive Weather Dashboard")
st.markdown("""
Welcome to the interactive weather dashboard!  

**How to use this webpage:**  
1. Click on the map below to select any location in the world.  
2. After clicking, the app will show the **current weather** for that location.  
3. You can also view the **temperature trends for the next 24 hours** and the **daily forecast for the next 7 days**.  

This app uses the [Open-Meteo API](https://open-meteo.com/) to fetch weather data in real-time.
""")

# ====== MAP ======
m = folium.Map(location=[37.5665, 126.9780], zoom_start=6)
st.write("Click on the map to select a location and view weather information")
map_data = st_folium(m, width=700, height=500)

if map_data and map_data['last_clicked']:
    lat = map_data['last_clicked']['lat']
    lon = map_data['last_clicked']['lng']
    st.write(f"Selected location: Latitude {lat:.4f}, Longitude {lon:.4f}")

    # ====== FETCH WEATHER DATA ======
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&"
        f"hourly=temperature_2m,precipitation,winddirection_10m,windspeed_10m&"
        f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    )
    response = requests.get(url)
    data = response.json()

    # ====== CURRENT WEATHER ======
    if "current_weather" in data:
        weather = data["current_weather"]
        st.subheader("Current Weather")
        st.write(f"Temperature: {weather['temperature']}°C")
        st.write(f"Wind Speed: {weather['windspeed']} km/h")
        st.write(f"Wind Direction: {weather['winddirection']}°")
        st.write(f"Weather Code: {weather['weathercode']}")
    else:
        st.error("Unable to fetch current weather data")

    # ====== 7-DAY FORECAST ======
    if "daily" in data:
        daily = data["daily"]
        df_daily = pd.DataFrame({
            "Date": daily["time"],
            "Max Temp (°C)": daily["temperature_2m_max"],
            "Min Temp (°C)": daily["temperature_2m_min"],
            "Precipitation (mm)": daily["precipitation_sum"]
        })
        st.subheader("7-Day Forecast")
        st.dataframe(df_daily)

        # Plot max/min temperature line chart
        plt.figure(figsize=(8,3))
        plt.plot(df_daily["Date"], df_daily["Max Temp (°C)"], marker='o', label="Max Temp")
        plt.plot(df_daily["Date"], df_daily["Min Temp (°C)"], marker='o', label="Min Temp")
        plt.title("7-Day Temperature Trends")
        plt.xlabel("Date")
        plt.ylabel("Temperature (°C)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        st.pyplot(plt)

    # ====== NEXT 24 HOURS TEMPERATURE ======
    if "hourly" in data:
        hourly = data["hourly"]
        df_hourly = pd.DataFrame({
            "Time": hourly["time"],
            "Temperature (°C)": hourly["temperature_2m"],
            "Precipitation (mm)": hourly["precipitation"],
            "Wind Speed (km/h)": hourly["windspeed_10m"],
            "Wind Direction (°)": hourly["winddirection_10m"]
        })
        st.subheader("Next 24 Hours Temperature Trend")
        df_24h = df_hourly.head(24)
        plt.figure(figsize=(8,3))
        plt.plot(pd.to_datetime(df_24h["Time"]), df_24h["Temperature (°C)"], marker='o', color='orange')
        plt.title("Next 24 Hours Temperature")
        plt.xlabel("Time")
        plt.ylabel("Temperature (°C)")
        plt.xticks(rotation=45)
        plt.grid(True)
        st.pyplot(plt)

