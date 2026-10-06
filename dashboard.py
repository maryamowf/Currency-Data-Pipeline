import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Currency Data Pipeline Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS for Professional Design
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #00d26a;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    .stMetric label { font-size: 14px !important; color: #a0a0a0 !important; }
    .stMetric .metric-value { font-size: 24px !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Database Connection
@st.cache_data(ttl=30)
def load_data():
    server = '.'
    database = 'CurrencyDB'
    connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(connection_string)
    
    query = "SELECT * FROM exchange_rates ORDER BY fetched_at ASC"
    df = pd.read_sql(query, engine)
    df['fetched_at'] = pd.to_datetime(df['fetched_at'])
    return df

try:
    df = load_data()
    
    # Header Section
    st.title("⚡ Real-Time Currency Pipeline Monitor")
    st.caption("Automated ETL Pipeline: REST API ➔ SQL Server ➔ Streamlit Dashboard")
    st.divider()
    
    # Metrics Overview
    st.subheader("📌 Latest Exchange Rates (vs USD)")
    
    latest_time = df['fetched_at'].max()
    latest_df = df[df['fetched_at'] == latest_time]
    
    cols = st.columns(len(latest_df))
    currency_flags = {
        'EGP': '🇪🇬', 'EUR': '🇪🇺', 'GBP': '🇬🇧', 
        'SAR': '🇸🇦', 'AED': '🇦🇪', 'KWD': '🇰🇼'
    }
    
    for idx, (_, row) in enumerate(latest_df.iterrows()):
        curr = row['target_currency']
        rate = row['exchange_rate']
        flag = currency_flags.get(curr, '🌐')
        
        with cols[idx]:
            st.metric(
                label=f"{flag} {curr}",
                value=f"{rate:,.2f}"
            )
            
    st.divider()
    
    # Analytics Charts
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📊 Rate Comparison")
        fig_bar = px.bar(
            latest_df,
            x='target_currency',
            y='exchange_rate',
            color='target_currency',
            text_auto='.2f',
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_bar.update_layout(showlegend=False, xaxis_title="Currency", yaxis_title="Exchange Rate (USD)")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_right:
        st.subheader("📈 Historical Trend")
        fig_line = px.line(
            df,
            x='fetched_at',
            y='exchange_rate',
            color='target_currency',
            markers=True,
            template="plotly_dark"
        )
        fig_line.update_layout(xaxis_title="Fetch Timestamp", yaxis_title="Rate")
        st.plotly_chart(fig_line, use_container_width=True)

    # Raw Data Table
    st.subheader("💾 Database Records (SQL Server)")
    st.dataframe(df.sort_values('fetched_at', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error connecting to Database: {e}")