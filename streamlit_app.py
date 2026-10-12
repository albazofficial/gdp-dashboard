"""
Global GDP Macroeconomic Intelligence Platform.
Streamlit Controller consuming modular domain engines.
"""

import sys
from pathlib import Path

# Force Python path to include project root for Streamlit Cloud
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Import our new modular core engines
from src.pipeline.loader import load_and_transform_gdp_data
from src.core.metrics import calculate_cagr, calculate_yoy_growth, calculate_volatility

from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Import our new modular core engines
from src.pipeline.loader import load_and_transform_gdp_data
from src.core.metrics import calculate_cagr, calculate_yoy_growth, calculate_volatility

# Page Setup
st.set_page_config(
    page_title="Global GDP Analytics Engine",
    page_icon="🌍",
    layout="wide"
)

DATA_PATH = Path(__file__).parent / 'data/gdp_data.csv'

@st.cache_data(ttl="1d", show_spinner="Normalizing macroeconomic records...")
def get_dataset() -> pd.DataFrame:
    return load_and_transform_gdp_data(DATA_PATH)

try:
    gdp_df = get_dataset()
except Exception as err:
    st.error(f"Runtime Engine Failure: {err}")
    st.stop()

# Header
st.title("🌍 Global GDP Macroeconomic Intelligence Platform")
st.caption("Engineered longitudinal econometric profiling (World Bank Dataset 1960–2022)")

# Sidebar Filter Controls
st.sidebar.header("Filter & Controls")

min_year = int(gdp_df['Year'].min())
max_year = int(gdp_df['Year'].max())

from_year, to_year = st.sidebar.slider(
    "Analysis Window",
    min_value=min_year,
    max_value=max_year,
    value=(1990, max_year)
)

all_countries = sorted(gdp_df['Country Name'].unique())
default_selection = ['United States', 'China', 'Germany', 'Japan', 'United Kingdom', 'Egypt, Arab Rep.']
valid_defaults = [c for c in default_selection if c in all_countries]

selected_countries = st.sidebar.multiselect(
    "Select Benchmark Nations",
    options=all_countries,
    default=valid_defaults
)

if not selected_countries:
    st.warning("⚠️ Please select at least one nation from the sidebar.")
    st.stop()

# Filter Query
filtered_df = gdp_df[
    (gdp_df['Country Name'].isin(selected_countries)) &
    (gdp_df['Year'] >= from_year) &
    (gdp_df['Year'] <= to_year)
]

# Tabs Organization
tab_trends, tab_comparison, tab_table = st.tabs(["📈 Growth & Trajectory", "📊 Comparative Delta", "📋 Raw Ledger"])

with tab_trends:
    st.subheader("Historical GDP Trajectory (Current US$)")
    fig = px.line(
        filtered_df,
        x='Year',
        y='GDP',
        color='Country Name',
        markers=True,
        labels={'GDP': 'GDP (USD)', 'Year': 'Year'},
        template="plotly_dark"
    )
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True)

with tab_comparison:
    st.subheader(f"Macroeconomic Delta Summary ({from_year} vs {to_year})")
    num_years = to_year - from_year
    cols = st.columns(min(len(selected_countries), 4))
    
    for idx, country in enumerate(selected_countries):
        country_data = gdp_df[gdp_df['Country Name'] == country].sort_values('Year')
        
        start_row = country_data[country_data['Year'] == from_year]
        end_row = country_data[country_data['Year'] == to_year]
        
        start_gdp = start_row['GDP'].values[0] if not start_row.empty else np.nan
        end_gdp = end_row['GDP'].values[0] if not end_row.empty else np.nan
        
        cagr = calculate_cagr(start_gdp, end_gdp, num_years)
        
        with cols[idx % len(cols)]:
            display_val = f"${end_gdp / 1e9:,.2f} B" if not pd.isna(end_gdp) else "N/A"
            cagr_delta = f"{cagr * 100:.2f}% CAGR" if not pd.isna(cagr) else "N/A"
            st.metric(label=country, value=display_val, delta=cagr_delta)

with tab_table:
    st.subheader("Normalized Time-Series Ledger")
    st.dataframe(
        filtered_df.sort_values(by=['Year', 'GDP'], ascending=[False, False]),
        use_container_width=True
    )
