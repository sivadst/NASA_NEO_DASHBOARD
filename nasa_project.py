import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(layout='wide')
st.title("🌌 NASA NEO Tracking & Insights Dashboard")
st.markdown("Explore asteroid data, approach speeds, distances, and hazard insights using SQL-powered queries.")

# Connect to DB
conn = sqlite3.connect("Asteroid_Data.db")
cursor = conn.cursor()

def show_query(query):
    df = pd.read_sql_query(query, conn)
    st.dataframe(df)

# 🎛️ Main Filter Panel
with st.expander("🔧 Query & Filter Settings", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        mag_range = st.slider("Absolute Magnitude (H)", 10.0, 35.0, (15.0, 30.0))
        au_range = st.slider("Astronomical Unit", 0.0, 1.5, (0.05, 1.0))
        hazardous_only = st.checkbox("☄️ Only Hazardous Asteroids")

    with col2:
        diam_range = st.slider("Estimated Diameter (km)", 0.0, 1.0, (0.01, 0.5))
        start_date = st.date_input("Start Date", datetime(2024, 1, 1))
        end_date = st.date_input("End Date", datetime(2024, 12, 31))

    with col3:
        vel_range = st.slider("Velocity (kmph)", 0.0, 150000.0, (10000.0, 50000.0))

# SQL Filter Query
filters = f'''
SELECT a.name, a.absolute_magnitude_h, a.estimated_diameter_min_km,
       a.estimated_diameter_max_km, a.is_potentially_hazardous_asteroid,
       ca.close_approach_date, ca.relative_velocity_kmph,
       ca.astronomical, ca.miss_distance_km
FROM asteroids a
JOIN close_approach ca ON a.id = ca.neo_reference_id
WHERE
    a.absolute_magnitude_h BETWEEN {mag_range[0]} AND {mag_range[1]} AND
    a.estimated_diameter_min_km >= {diam_range[0]} AND
    a.estimated_diameter_max_km <= {diam_range[1]} AND
    ca.relative_velocity_kmph BETWEEN {vel_range[0]} AND {vel_range[1]} AND
    ca.astronomical BETWEEN {au_range[0]} AND {au_range[1]} AND
    ca.close_approach_date BETWEEN "{start_date}" AND "{end_date}"
'''
if hazardous_only:
    filters += " AND a.is_potentially_hazardous_asteroid = 1"

st.success("🔍 Showing Filtered Results")
show_query(filters)

# 📈 Query Selector (in center now!)
query_option = st.selectbox("📌 Choose Predefined Query", [
    "Count approaches per asteroid",
    "Average velocity per asteroid",
    "Top 10 fastest asteroids",
    "Hazardous asteroids > 3 approaches",
    "Month with most approaches",
    "Fastest asteroid ever",
    "Sort by max diameter",
    "Closest approach trend",
    "Closest approach details",
    "Asteroids > 50,000 km/h",
    "Approach count per month",
    "Brightest asteroid",
    "Hazardous vs Non-hazardous",
    "Passed closer than Moon",
    "Came within 0.05 AU",
    "Bloozer 1: Top 5 by brightness",
    "Bloozer 2: Most missed close call",
    "Bloozer 3: Approaches by orbiting body",
    "Bloozer 4: Avg AU for hazardous",
    "Bloozer 5: Max diameter per month",
    "Bloozer 6: First ever approach",
    "Bloozer 7: Last known approach"
])

queries = {
    "Count approaches per asteroid": '''SELECT neo_reference_id, COUNT(*) AS approach_count FROM close_approach GROUP BY neo_reference_id''',
    "Average velocity per asteroid": '''SELECT neo_reference_id, AVG(relative_velocity_kmph) AS avg_velocity FROM close_approach GROUP BY neo_reference_id''',
    "Top 10 fastest asteroids": '''SELECT neo_reference_id, MAX(relative_velocity_kmph) AS max_velocity FROM close_approach GROUP BY neo_reference_id ORDER BY max_velocity DESC LIMIT 10''',
    "Hazardous asteroids > 3 approaches": '''SELECT ca.neo_reference_id, COUNT(*) FROM close_approach ca JOIN asteroids a ON ca.neo_reference_id = a.id WHERE a.is_potentially_hazardous_asteroid = 1 GROUP BY ca.neo_reference_id HAVING COUNT(*) > 3''',
    "Month with most approaches": '''SELECT STRFTIME('%m', close_approach_date) AS month, COUNT(*) AS count FROM close_approach GROUP BY month ORDER BY count DESC LIMIT 1''',
    "Fastest asteroid ever": '''SELECT name, MAX(relative_velocity_kmph) FROM close_approach JOIN asteroids ON id = neo_reference_id''',
    "Sort by max diameter": '''SELECT name, estimated_diameter_max_km FROM asteroids ORDER BY estimated_diameter_max_km DESC''',
    "Closest approach trend": '''SELECT name, close_approach_date, miss_distance_km FROM close_approach JOIN asteroids ON id = neo_reference_id ORDER BY close_approach_date ASC, miss_distance_km ASC''',
    "Closest approach details": '''SELECT name, close_approach_date, MIN(miss_distance_km) FROM close_approach JOIN asteroids ON id = neo_reference_id GROUP BY name''',
    "Asteroids > 50,000 km/h": '''SELECT name, relative_velocity_kmph FROM close_approach JOIN asteroids ON id = neo_reference_id WHERE relative_velocity_kmph > 50000''',
    "Approach count per month": '''SELECT STRFTIME('%m', close_approach_date) AS month, COUNT(*) FROM close_approach GROUP BY month''',
    "Brightest asteroid": '''SELECT name, MIN(absolute_magnitude_h) FROM asteroids''',
    "Hazardous vs Non-hazardous": '''SELECT is_potentially_hazardous_asteroid, COUNT(*) FROM asteroids GROUP BY is_potentially_hazardous_asteroid''',
    "Passed closer than Moon": '''SELECT name, close_approach_date, miss_distance_lunar FROM close_approach JOIN asteroids ON id = neo_reference_id WHERE miss_distance_lunar < 1''',
    "Came within 0.05 AU": '''SELECT name, close_approach_date, astronomical FROM close_approach JOIN asteroids ON id = neo_reference_id WHERE astronomical < 0.05''',
    "Bloozer 1: Top 5 by brightness": '''SELECT name, absolute_magnitude_h FROM asteroids ORDER BY absolute_magnitude_h ASC LIMIT 5''',
    "Bloozer 2: Most missed close call": '''SELECT name, MAX(miss_distance_km) FROM close_approach JOIN asteroids ON id = neo_reference_id''',
    "Bloozer 3: Approaches by orbiting body": '''SELECT orbiting_body, COUNT(*) FROM close_approach GROUP BY orbiting_body''',
    "Bloozer 4: Avg AU for hazardous": '''SELECT AVG(astronomical) FROM close_approach JOIN asteroids ON id = neo_reference_id WHERE is_potentially_hazardous_asteroid = 1''',
    "Bloozer 5: Max diameter per month": '''SELECT STRFTIME('%m', close_approach_date) AS month, MAX(estimated_diameter_max_km) FROM close_approach JOIN asteroids ON id = neo_reference_id GROUP BY month''',
    "Bloozer 6: First ever approach": '''SELECT name, MIN(close_approach_date) FROM close_approach JOIN asteroids ON id = neo_reference_id''',
    "Bloozer 7: Last known approach": '''SELECT name, MAX(close_approach_date) FROM close_approach JOIN asteroids ON id = neo_reference_id'''
}

st.subheader(f"📌 Result: {query_option}")
show_query(queries[query_option])
