import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from PIL import Image
import io

# Set up the app title and icon
st.set_page_config(page_title="Advanced Weather Forecast", page_icon="⛅", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .weather-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
    }
    .temperature {
        font-size: 48px;
        font-weight: bold;
        color: #1e88e5;
    }
    .weather-icon {
        font-size: 36px;
    }
    .forecast-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        margin: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        height: 44px;
        transition: all 0.3s ease;
        background-color: #1e88e5;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #1565c0;
        transform: scale(1.1);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        color:white !important;
    }
    
    .button-container {
        display: flex;
        align-items: center;
        height: 100%;
        padding-top: 10px;
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        height: 44px;
        border-radius: 8px;
        border: 1px solid #ced4da;
        padding: 10px 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to get current weather data
def get_weather(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data: {e}")
        return None

# Function to get 5-day forecast
def get_forecast(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'cnt': 40  # 5 days * 8 forecasts per day
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching forecast data: {e}")
        return None

# Function to get air quality data
def get_air_quality(lat, lon, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None  # Silently fail as not all users may have access to this API

# Function to display UV index with recommendations
def display_uv_info(uv_index):
    uv_info = {
        'level': '',
        'color': '',
        'recommendation': ''
    }
    
    if uv_index <= 2:
        uv_info['level'] = 'Low'
        uv_info['color'] = 'green'
        uv_info['recommendation'] = 'Wear sunglasses on bright days'
    elif 3 <= uv_index <= 5:
        uv_info['level'] = 'Moderate'
        uv_info['color'] = 'yellow'
        uv_info['recommendation'] = 'Stay in shade near midday. Wear sunscreen, a hat, and sunglasses.'
    elif 6 <= uv_index <= 7:
        uv_info['level'] = 'High'
        uv_info['color'] = 'orange'
        uv_info['recommendation'] = 'Reduce time in the sun between 10am-4pm. Apply sunscreen every 2 hours.'
    elif 8 <= uv_index <= 10:
        uv_info['level'] = 'Very High'
        uv_info['color'] = 'red'
        uv_info['recommendation'] = 'Minimize sun exposure between 10am-4pm. Use SPF 30+ sunscreen.'
    else:
        uv_info['level'] = 'Extreme'
        uv_info['color'] = 'purple'
        uv_info['recommendation'] = 'Avoid sun exposure between 10am-4pm. Full protective clothing recommended.'
    
    return uv_info

# Function to display weather data
def display_weather(weather_data, forecast_data=None, air_quality_data=None):
    if not weather_data:
        return
    
    # Extract current weather data
    city = weather_data['name']
    country = weather_data['sys']['country']
    temp = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    humidity = weather_data['main']['humidity']
    pressure = weather_data['main']['pressure']
    wind_speed = weather_data['wind']['speed']
    wind_deg = weather_data['wind'].get('deg', 0)
    weather_desc = weather_data['weather'][0]['description']
    weather_main = weather_data['weather'][0]['main']
    icon_code = weather_data['weather'][0]['icon']
    timestamp = weather_data['dt']
    visibility = weather_data.get('visibility', 'N/A')
    clouds = weather_data.get('clouds', {}).get('all', 0)
    sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime("%H:%M")
    sunset = datetime.fromtimestamp(weather_data['sys']['sunset']).strftime("%H:%M")
    
    # Get emoji for weather condition
    weather_emojis = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Fog': '🌁'
    }
    emoji = weather_emojis.get(weather_main, '🌈')
    
    # Convert timestamp to readable date/time
    date_time = datetime.fromtimestamp(timestamp).strftime("%A, %B %d, %Y %H:%M")
    
    # Display current weather information
    st.markdown(f"<div class='weather-container'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"<div class='temperature'>{temp}°C</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='big-font'>Feels like: {feels_like}°C</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='big-font'>{weather_desc.capitalize()} {emoji}</div>", unsafe_allow_html=True)
        
        # Display weather icon from OpenWeatherMap
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
        icon_response = requests.get(icon_url)
        if icon_response.status_code == 200:
            icon_img = Image.open(io.BytesIO(icon_response.content))
            st.image(icon_img, width=100)
    
    with col2:
        st.markdown(f"### {emoji} Weather in {city}, {country}")
        st.caption(f"Updated on {date_time}")
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("Humidity", f"{humidity}%", "💧")
        with cols[1]:
            st.metric("Wind Speed", f"{wind_speed} m/s", "🌬️")
        with cols[2]:
            st.metric("Pressure", f"{pressure} hPa", "📊")
        with cols[3]:
            st.metric("Visibility", f"{visibility/1000 if visibility != 'N/A' else 'N/A'} km" if visibility != 'N/A' else 'N/A', "👀")
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("Sunrise", sunrise, "🌅")
        with cols[1]:
            st.metric("Sunset", sunset, "🌇")
        with cols[2]:
            st.metric("Cloudiness", f"{clouds}%", "☁️")
        with cols[3]:
            if wind_deg != 0:
                wind_dir = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][round(wind_deg / 45) % 8]
                st.metric("Wind Direction", wind_dir, "🧭")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display additional sections if data is available
    if forecast_data and forecast_data.get('cod') == '200':
        display_forecast(forecast_data)
    
    if air_quality_data:
        display_air_quality(air_quality_data)
    
    # Add weather map
    st.subheader("🌍 Weather Map")
    st.write("See current weather conditions around the world:")
    st.components.v1.iframe("https://openweathermap.org/weathermap?basemap=map&cities=true&layer=clouds&lat=30&lon=0&zoom=2", 
                           height=400, scrolling=True)

# Function to display forecast data
def display_forecast(forecast_data):
    st.subheader("📅 5-Day Forecast")
    
    # Process forecast data
    forecast_list = forecast_data['list']
    df = pd.DataFrame([{
        'datetime': datetime.fromtimestamp(item['dt']),
        'date': datetime.fromtimestamp(item['dt']).strftime('%A, %b %d'),
        'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
        'temp': item['main']['temp'],
        'feels_like': item['main']['feels_like'],
        'humidity': item['main']['humidity'],
        'weather': item['weather'][0]['main'],
        'description': item['weather'][0]['description'],
        'icon': item['weather'][0]['icon'],
        'wind_speed': item['wind']['speed'],
        'clouds': item['clouds']['all']
    } for item in forecast_list])
    
    # Group by day
    df['day'] = df['datetime'].dt.date
    
    # Create tabs for each day
    tabs = st.tabs([day.strftime('%A, %b %d') for day in sorted(df['day'].unique())])
    
    for i, (day, day_data) in enumerate(df.groupby('day')):
        with tabs[i]:
            # Daily summary
            col1, col2 = st.columns([1, 3])
            with col1:
                avg_temp = round(day_data['temp'].mean(), 1)
                min_temp = round(day_data['temp'].min(), 1)
                max_temp = round(day_data['temp'].max(), 1)
                st.metric("Avg Temp", f"{avg_temp}°C")
                st.metric("Range", f"{min_temp}°C - {max_temp}°C")
            
            with col2:
                # Temperature chart
                fig = px.line(day_data, x='time', y='temp', 
                             title=f"Temperature Variation on {day.strftime('%A, %b %d')}",
                             labels={'time': 'Time', 'temp': 'Temperature (°C)'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Hourly forecast cards
            st.subheader("Hourly Forecast")
            cols = st.columns(4)
            for j, (_, hour) in enumerate(day_data.iterrows()):
                with cols[j % 4]:
                    with st.container():
                        st.markdown(f"<div class='forecast-card'>", unsafe_allow_html=True)
                        st.write(f"**{hour['time']}**")
                        st.write(f"**{hour['temp']}°C**")
                        st.write(f"{hour['description'].capitalize()}")
                        st.write(f"💧 {hour['humidity']}%")
                        st.write(f"🌬️ {hour['wind_speed']} m/s")
                        st.markdown("</div>", unsafe_allow_html=True)

# Function to display air quality data
def display_air_quality(air_quality_data):
    st.subheader("🌬️ Air Quality Index (AQI)")
    
    aqi = air_quality_data['list'][0]['main']['aqi']
    components = air_quality_data['list'][0]['components']
    
    aqi_levels = {
        1: {'label': 'Good', 'color': 'green', 'description': 'Air quality is satisfactory.'},
        2: {'label': 'Fair', 'color': 'yellow', 'description': 'Air quality is acceptable.'},
        3: {'label': 'Moderate', 'color': 'orange', 'description': 'Sensitive groups may experience health effects.'},
        4: {'label': 'Poor', 'color': 'red', 'description': 'Everyone may begin to experience health effects.'},
        5: {'label': 'Very Poor', 'color': 'purple', 'description': 'Health warnings of emergency conditions.'}
    }
    
    level = aqi_levels.get(aqi, {'label': 'Unknown', 'color': 'gray', 'description': 'No data available.'})
    
    cols = st.columns(5)
    with cols[0]:
        st.metric("AQI", aqi, level['label'])
    with cols[1]:
        st.metric("CO", f"{components['co']} μg/m³", "Carbon Monoxide")
    with cols[2]:
        st.metric("NO₂", f"{components['no2']} μg/m³", "Nitrogen Dioxide")
    with cols[3]:
        st.metric("O₃", f"{components['o3']} μg/m³", "Ozone")
    with cols[4]:
        st.metric("PM2.5", f"{components['pm2_5']} μg/m³", "Fine Particles")
    
    st.info(f"**{level['label']}**: {level['description']}")
    
    # Health recommendations
    if aqi >= 3:
        st.warning("""
        **Health Recommendations:**
        - Reduce outdoor activities
        - Keep windows closed
        - Use air purifiers if available
        - Sensitive groups should take extra precautions
        """)

# Main app
def main():
    st.title("⛅ Advanced Weather Forecast App")
    st.write("Get comprehensive weather information for any location worldwide!")
    
    # Get API key
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        st.error("""
            API key not found. Please set up your OpenWeatherMap API key.
            
            1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
            2. Get your API key
            3. Set it as an environment variable named OPENWEATHER_API_KEY
        """)
        st.stop()
    
    # City input with geolocation option
    col1, col2 = st.columns([4, 1])
    with col1:
        city = st.text_input("Enter a city name:", placeholder="E.g., London, Tokyo, New York")
    with col2:
        st.markdown("<div class='button-container'>", unsafe_allow_html=True)
        if st.button("Search Location"):
            try:
                # This requires HTTPS in production
                location = st.session_state.get('location', None)
                if location:
                    lat, lon = location['latitude'], location['longitude']
                    reverse_geocode_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
                    response = requests.get(reverse_geocode_url)
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            city = data[0].get('name', '')
                            st.experimental_rerun()
            except:
                st.warning("Location access not available or denied")
        st.markdown("</div>", unsafe_allow_html=True)
    
    if city:
        if city.lower() == 'exit':
            st.info("Thank you for using the Weather Forecast App. Goodbye!")
            return
        
        with st.spinner(f"Fetching weather data for {city}..."):
            # Get current weather
            weather_data = get_weather(city, api_key)
            
            if weather_data and weather_data.get('cod') == 200:
                # Get forecast if current weather is successful
                forecast_data = get_forecast(city, api_key)
                
                # Get air quality if coordinates are available
                air_quality_data = None
                if 'coord' in weather_data:
                    air_quality_data = get_air_quality(
                        weather_data['coord']['lat'],
                        weather_data['coord']['lon'],
                        api_key
                    )
                
                display_weather(weather_data, forecast_data, air_quality_data)
            elif weather_data and weather_data.get('cod') == '404':
                st.error(f"City '{city}' not found. Please check the spelling and try again.")
            else:
                st.error("Could not retrieve weather data. Please try again later.")

if __name__ == "__main__":
    main()