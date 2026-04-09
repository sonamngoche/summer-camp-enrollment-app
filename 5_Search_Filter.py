import streamlit as st
import psycopg2
import psycopg2.extras
from datetime import date

st.set_page_config(page_title="Search & Filter", layout="wide")

# -----------------------------
# Database Connection
# -----------------------------
def get_connection():
    return psycopg2.connect(
        st.secrets["DB_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor
    )

# -----------------------------
# Query Helpers
# -----------------------------
def search_campers_by_last_name(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, first_name, last_name, age, guardian_email, guardian_phone
        FROM campers
        WHERE last_name ILIKE %s
        ORDER BY last_name;
    """, (f"%{query}%",))
    rows = cur.fetchall()
    conn.close()
    return rows

def filter_camps_by_date(start, end):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.camp_name, c.start_date, c.end_date, c.capacity,
               i.first_name AS instructor_first, i.last_name AS instructor_last
        FROM camps c
        LEFT JOIN instructors i ON c.instructor_id = i.id
        WHERE c.start_date >= %s AND c.end_date <= %s
        ORDER BY c.start_date;
    """, (start, end))
    rows = cur.fetchall()
    conn.close()
    return rows

# -----------------------------
# Page UI
# -----------------------------
st.title("Search & Filter")
st.markdown("Use the tools below to search campers or filter camps by date range.")

# -----------------------------
# Search Campers
# -----------------------------
st.subheader("Search Campers by Last Name")

search_query = st.text_input("Enter last name (partial or full):")

if search_query:
    results = search_campers_by_last_name(search_query)
    if results:
        st.write(f"Found **{len(results)}** matching campers.")
        st.table(results)
    else:
        st.info("No campers found with that last name.")

st.markdown("---")

# -----------------------------
# Filter Camps by Date Range
# -----------------------------
st.subheader("Filter Camps by Date Range")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date", value
