# 🌍 Renewable Energy Site Analyzer

A comprehensive web application for assessing renewable energy potential (wind and solar) at any location on Earth using historical meteorological data.

## Features

- **Interactive Map**: Select any location on Earth with precise latitude/longitude inputs
- **Real-time Data**: Fetches historical weather data from NASA POWER API
- **Wind Analysis**: 
  - Average and maximum wind speeds
  - Wind rose diagram showing directional frequency
  - Wind energy potential assessment
- **Solar Analysis**:
  - Average and maximum solar irradiance
  - Daily solar radiation trends
  - Solar energy potential assessment
- **Visualizations**:
  - Time series charts for wind and solar data
  - Wind rose diagram for directional analysis
  - Interactive maps with location markers
- **Data Export**: Download raw data as CSV for further analysis

## Installation

1. Clone this repository:
```bash
git clone https://github.com/loisjlee23/geo-visualiser.git
cd geo-visualiser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your default web browser. Then:

1. Enter the **latitude** and **longitude** of your location of interest
2. Select the **year** for historical data analysis
3. Click the **"Analyze Location"** button
4. Review the results including:
   - Key metrics (average wind speed, solar radiation)
   - Energy potential assessments
   - Temporal trends charts
   - Wind rose diagram
   - Raw data table

## Data Source

This application uses the **NASA POWER (Prediction Of Worldwide Energy Resources)** API, which provides:
- Wind Speed at 10m height (m/s)
- Wind Direction (degrees)
- All-Sky Surface Shortwave Downward Irradiance (kWh/m²/day)

Data is available globally with daily resolution for multiple years.

## Technology Stack

- **Streamlit**: Web application framework
- **Folium**: Interactive maps
- **Plotly**: Interactive charts
- **Windrose**: Wind rose diagrams
- **Pandas**: Data manipulation
- **NASA POWER API**: Meteorological data source

## Energy Potential Guidelines

### Wind Energy Assessment:
- **Excellent** (>7.5 m/s): Prime location for wind turbines
- **Good** (6.5-7.5 m/s): Suitable for commercial wind energy
- **Fair** (5-6.5 m/s): Moderate potential, suitable for small turbines
- **Marginal** (3-5 m/s): Limited wind energy potential
- **Poor** (<3 m/s): Not recommended for wind energy

### Solar Energy Assessment:
- **Excellent** (>5 kWh/m²/day): Optimal for solar installations
- **Good** (4-5 kWh/m²/day): Very suitable for solar panels
- **Fair** (3-4 kWh/m²/day): Moderate solar potential
- **Poor** (<3 kWh/m²/day): Limited solar potential

## License

This project is open source and available for educational and research purposes.

## Acknowledgments

- NASA POWER Project for providing free access to global meteorological data
- Streamlit for the excellent web framework
- The open-source community for the visualization libraries
