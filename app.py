import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from windrose import WindroseAxes
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="Renewable Energy Site Analyzer",
    page_icon="🌍",
    layout="wide"
)

# Title
st.title("🌍 Renewable Energy Site Analyzer")
st.markdown("Assess the renewable energy potential (wind and solar) for any location on Earth")

# Sidebar for user controls
st.sidebar.header("Location Controls")

# Input widgets for coordinates
latitude = st.sidebar.number_input(
    "Latitude",
    min_value=-90.0,
    max_value=90.0,
    value=40.7128,
    step=0.0001,
    format="%.4f",
    help="Enter latitude between -90 and 90"
)

longitude = st.sidebar.number_input(
    "Longitude",
    min_value=-180.0,
    max_value=180.0,
    value=-74.0060,
    step=0.0001,
    format="%.4f",
    help="Enter longitude between -180 and 180"
)

# Year selection for data retrieval
current_year = datetime.now().year
year = st.sidebar.selectbox(
    "Select Year for Analysis",
    options=list(range(current_year - 1, current_year - 11, -1)),
    index=0,
    help="Select which year's data to analyze"
)

# Analyze button
analyze_button = st.sidebar.button("🔍 Analyze Location", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**About:**")
st.sidebar.info(
    "This tool uses NASA POWER API to retrieve meteorological data "
    "and calculate renewable energy potential for any location."
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Author:** Lois Lee")
st.sidebar.markdown("**Date:** October 2025")


# Phase II: Interactive Map
def create_map(lat, lon):
    """Create an interactive map centered on the given coordinates"""
    m = folium.Map(
        location=[lat, lon],
        zoom_start=10,
        tiles="OpenStreetMap"
    )
    
    # Add marker
    folium.Marker(
        [lat, lon],
        popup=f"Lat: {lat:.4f}, Lon: {lon:.4f}",
        tooltip="Selected Location",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    
    return m


# Display the map
st.subheader("📍 Selected Location")
map_obj = create_map(latitude, longitude)
st_folium(map_obj, width=1200, height=400)


# Phase III: Data Retrieval Function
@st.cache_data(ttl=3600)
def fetch_nasa_power_data(lat, lon, year):
    """
    Fetch meteorological data from NASA POWER API
    
    Parameters:
    - lat: latitude
    - lon: longitude
    - year: year for data retrieval
    
    Returns:
    - DataFrame with daily wind speed, wind direction, and solar irradiance
    """
    # NASA POWER API endpoint
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Parameters we need
    parameters = "WS10M,WD10M,ALLSKY_SFC_SW_DWN"
    
    # Date range
    start_date = f"{year}0101"
    end_date = f"{year}1231"
    
    # Construct the API URL
    url = f"{base_url}?parameters={parameters}&community=RE&longitude={lon}&latitude={lat}&start={start_date}&end={end_date}&format=JSON"
    
    try:
        # Make the request
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Parse the response
        if 'properties' in data and 'parameter' in data['properties']:
            params = data['properties']['parameter']
            
            # Extract data
            wind_speed = params.get('WS10M', {})
            wind_direction = params.get('WD10M', {})
            solar_irradiance = params.get('ALLSKY_SFC_SW_DWN', {})
            
            # Create DataFrame
            df = pd.DataFrame({
                'date': pd.to_datetime(list(wind_speed.keys()), format='%Y%m%d'),
                'wind_speed': list(wind_speed.values()),
                'wind_direction': list(wind_direction.values()),
                'solar_irradiance': list(solar_irradiance.values())
            })
            
            # Remove any invalid values (NASA uses -999 for missing data)
            df = df.replace(-999, np.nan)
            
            return df
        else:
            st.error("Unexpected data format from API")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None


# Phase IV: Analysis Functions
def calculate_metrics(df):
    """
    Calculate summary metrics from the data
    
    Parameters:
    - df: DataFrame with meteorological data
    
    Returns:
    - dict with calculated metrics
    """
    metrics = {
        'avg_wind_speed': df['wind_speed'].mean(),
        'avg_solar_radiation': df['solar_irradiance'].mean(),
        'max_wind_speed': df['wind_speed'].max(),
        'max_solar_radiation': df['solar_irradiance'].max(),
        'total_solar_energy': df['solar_irradiance'].sum(),
    }
    
    return metrics


# Phase V: Visualization Functions
def create_wind_rose(df):
    """
    Create a wind rose chart
    
    Parameters:
    - df: DataFrame with wind speed and direction data
    
    Returns:
    - matplotlib figure
    """
    # Remove NaN values
    clean_df = df[['wind_speed', 'wind_direction']].dropna()
    
    if len(clean_df) == 0:
        return None
    
    # Create wind rose
    fig = plt.figure(figsize=(10, 8))
    ax = WindroseAxes.from_ax(fig=fig)
    ax.bar(
        clean_df['wind_direction'],
        clean_df['wind_speed'],
        normed=True,
        opening=0.8,
        edgecolor='white',
        cmap=plt.cm.viridis
    )
    ax.set_legend(title="Wind Speed (m/s)", bbox_to_anchor=(1.1, 1.0))
    ax.set_title("Wind Rose Diagram", fontsize=14, fontweight='bold', pad=20)
    
    return fig


def create_time_series_charts(df):
    """
    Create time series charts for wind and solar data
    
    Parameters:
    - df: DataFrame with meteorological data
    
    Returns:
    - tuple of plotly figures (wind_fig, solar_fig)
    """
    # Wind speed time series
    wind_fig = go.Figure()
    wind_fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['wind_speed'],
        mode='lines',
        name='Wind Speed',
        line=dict(color='#1f77b4', width=1.5)
    ))
    wind_fig.update_layout(
        title="Daily Wind Speed Throughout the Year",
        xaxis_title="Date",
        yaxis_title="Wind Speed (m/s)",
        hovermode='x unified',
        height=350
    )
    
    # Solar irradiance time series
    solar_fig = go.Figure()
    solar_fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['solar_irradiance'],
        mode='lines',
        name='Solar Irradiance',
        line=dict(color='#ff7f0e', width=1.5),
        fill='tozeroy',
        fillcolor='rgba(255, 127, 14, 0.1)'
    ))
    solar_fig.update_layout(
        title="Daily Solar Irradiance Throughout the Year",
        xaxis_title="Date",
        yaxis_title="Solar Irradiance (kWh/m²/day)",
        hovermode='x unified',
        height=350
    )
    
    return wind_fig, solar_fig


# Phase VI: Main Analysis Workflow
if analyze_button:
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    with st.spinner(f"Fetching data from NASA POWER API for {year}..."):
        data_df = fetch_nasa_power_data(latitude, longitude, year)
    
    if data_df is not None and not data_df.empty:
        # Calculate metrics
        metrics = calculate_metrics(data_df)
        
        # Display metrics
        st.subheader("🎯 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Average Wind Speed",
                value=f"{metrics['avg_wind_speed']:.2f} m/s",
                help="Annual average wind speed at 10m height"
            )
        
        with col2:
            st.metric(
                label="Max Wind Speed",
                value=f"{metrics['max_wind_speed']:.2f} m/s",
                help="Maximum recorded wind speed"
            )
        
        with col3:
            st.metric(
                label="Average Solar Radiation",
                value=f"{metrics['avg_solar_radiation']:.2f} kWh/m²/day",
                help="Average daily solar irradiance"
            )
        
        with col4:
            st.metric(
                label="Max Solar Radiation",
                value=f"{metrics['max_solar_radiation']:.2f} kWh/m²/day",
                help="Maximum daily solar irradiance"
            )
        
        # Energy potential assessment
        st.markdown("---")
        st.subheader("⚡ Energy Potential Assessment")
        
        # Wind energy potential
        wind_assessment = ""
        if metrics['avg_wind_speed'] < 3:
            wind_assessment = "❌ **Poor** - Not suitable for wind energy"
        elif metrics['avg_wind_speed'] < 5:
            wind_assessment = "⚠️ **Marginal** - Limited wind energy potential"
        elif metrics['avg_wind_speed'] < 6.5:
            wind_assessment = "✅ **Fair** - Moderate wind energy potential"
        elif metrics['avg_wind_speed'] < 7.5:
            wind_assessment = "✅ **Good** - Good wind energy potential"
        else:
            wind_assessment = "🌟 **Excellent** - Excellent wind energy potential"
        
        # Solar energy potential
        solar_assessment = ""
        if metrics['avg_solar_radiation'] < 3:
            solar_assessment = "❌ **Poor** - Limited solar potential"
        elif metrics['avg_solar_radiation'] < 4:
            solar_assessment = "⚠️ **Fair** - Moderate solar potential"
        elif metrics['avg_solar_radiation'] < 5:
            solar_assessment = "✅ **Good** - Good solar potential"
        else:
            solar_assessment = "🌟 **Excellent** - Excellent solar potential"
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Wind Energy:** {wind_assessment}")
        with col2:
            st.info(f"**Solar Energy:** {solar_assessment}")
        
        # Time series charts
        st.markdown("---")
        st.subheader("📈 Temporal Trends")
        
        wind_fig, solar_fig = create_time_series_charts(data_df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(wind_fig, use_container_width=True)
        with col2:
            st.plotly_chart(solar_fig, use_container_width=True)
        
        # Wind rose chart
        st.markdown("---")
        st.subheader("🌹 Wind Rose Diagram")
        st.markdown("This diagram shows the frequency of wind from different directions and at various speeds.")
        
        wind_rose_fig = create_wind_rose(data_df)
        if wind_rose_fig:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.pyplot(wind_rose_fig)
        else:
            st.warning("Unable to generate wind rose - insufficient data")
        
        # Data table (optional, collapsible)
        st.markdown("---")
        with st.expander("📋 View Raw Data"):
            st.dataframe(data_df, use_container_width=True)
            
            # Download button
            csv = data_df.to_csv(index=False)
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name=f"renewable_energy_data_{latitude}_{longitude}_{year}.csv",
                mime="text/csv"
            )
        
        st.success(f"✅ Analysis complete! Data retrieved for {len(data_df)} days in {year}.")
    else:
        st.error("Failed to retrieve data. Please check your coordinates and try again.")
else:
    # Show instructions when no analysis has been run
    st.info("👈 Enter coordinates in the sidebar and click 'Analyze Location' to begin assessment.")
    
    st.markdown("---")
    st.subheader("ℹ️ How to Use")
    st.markdown("""
    1. **Enter Coordinates**: Input the latitude and longitude of your location of interest
    2. **Select Year**: Choose which year's historical data to analyze
    3. **Click Analyze**: Press the 'Analyze Location' button to retrieve data and generate results
    4. **Review Results**: Examine the metrics, charts, and energy potential assessment
    
    **Data Source:** NASA POWER (Prediction Of Worldwide Energy Resources)
    
    **Parameters Analyzed:**
    - Wind Speed at 10m height (m/s)
    - Wind Direction (degrees)
    - All-Sky Surface Shortwave Downward Irradiance (kWh/m²/day)
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; padding: 20px;'>"
    "Developed by <b>Lois Lee</b> | October 2025 | "
    "Data provided by NASA POWER API"
    "</div>",
    unsafe_allow_html=True
)

