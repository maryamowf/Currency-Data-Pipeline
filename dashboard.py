import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="Currency Data Pipeline Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric label { font-size: 14px !important; color: #a0a0a0 !important; }
    .stMetric .metric-value { font-size: 24px !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Function to fetch data (Try SQL Server first, fallback to REST API for online cloud)
@st.cache_data(ttl=60)
def fetch_data():
    try:
        from sqlalchemy import create_engine
        server = '.'
        database = 'CurrencyDB'
        connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        engine = create_engine(connection_string)
        query = "SELECT * FROM exchange_rates ORDER BY fetched_at ASC"
        df = pd.read_sql(query, engine)
        df['fetched_at'] = pd.to_datetime(df['fetched_at'])
        return df, "SQL Server (Local)"
    except Exception:
        # Online Cloud Fallback (Fetch directly from API)
        url = "https://open.er-api.com/v6/latest/USD"
        res = requests.get(url).json()
        rates = res.get("rates", {})
        targets = ['EGP', 'EUR', 'GBP', 'SAR', 'AED', 'KWD']
        
        now = datetime.now()
        data = []
        for target in targets:
            if target in rates:
                data.append({
                    'base_currency': 'USD',
                    'target_currency': target,
                    'exchange_rate': rates[target],
                    'api_last_update': res.get('time_last_update_utc', ''),
                    'fetched_at': now
                })
        df = pd.DataFrame(data)
        return df, "Live REST API (Cloud Mode)"

try:
    df, source = fetch_data()
    
    st.title("⚡ Real-Time Currency Pipeline Monitor")
    st.caption(f"Data Source: **{source}** | Automated Exchange Rates Monitor")
    st.divider()
    
    # Latest Metrics
    st.subheader("📌 Latest Exchange Rates (vs USD)")
    latest_time = df['fetched_at'].max()
    latest_df = df[df['fetched_at'] == latest_time]
    
    cols = st.columns(len(latest_df))
    flags = {'EGP': '🇪🇬', 'EUR': '🇪🇺', 'GBP': '🇬🇧', 'SAR': '🇸🇦', 'AED': '🇦🇪', 'KWD': '🇰🇼'}
    
    for idx, (_, row) in enumerate(latest_df.iterrows()):
        curr = row['target_currency']
        rate = row['exchange_rate']
        flag = flags.get(curr, '🌐')
        with cols[idx]:
            st.metric(label=f"{flag} {curr}", value=f"{rate:,.2f}")
            
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📊 Rate Comparison")
        fig_bar = px.bar(
            latest_df,
            x='target_currency',
            y='exchange_rate',
            color='target_currency',
            text_auto='.2f',
            template="plotly_dark"
        )
        fig_bar.update_layout(showlegend=False, xaxis_title="Currency", yaxis_title="Rate (USD)")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col2:
        st.subheader("📈 Historical Trend")
        fig_line = px.line(
            df,
            x='fetched_at',
            y='exchange_rate',
            color='target_currency',
            markers=True,
            template="plotly_dark"
        )
        fig_line.update_layout(xaxis_title="Timestamp", yaxis_title="Rate")
        st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("📋 Raw Data Table")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    
 
