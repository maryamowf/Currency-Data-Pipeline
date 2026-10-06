# ⚡ Real-Time Currency Data Pipeline & Analytics

An End-to-End Data Engineering project that fetches live exchange rates from a REST API, cleans and transforms the data, loads it into SQL Server (SSMS), and presents real-time analytics using a Streamlit Dashboard.

## 🏗️ Architecture
`REST API` ➔ `Python ETL Script` ➔ `SQL Server (SSMS)` ➔ `Streamlit Dashboard`

## 🛠️ Tech Stack
- **Language:** Python
- **Libraries:** Pandas, Requests, SQLAlchemy, PyODBC, Streamlit, Plotly
- **Database:** Microsoft SQL Server (SSMS)

## 📋 How to Run
1. Run `create_tables.sql` in SSMS to create the database and table.
2. Execute the ETL script: `python d.py`
3. Launch the dashboard: `streamlit run dashboard.py`
