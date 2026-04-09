import streamlit as st
import psycopg2
import psycopg2.extras
from datetime import date

st.set_page_config(page_title="Camp Dashboard", layout="wide")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"], cursor_factory=psycopg2.extras.RealDictCursor)

def get_total_campers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM campers;")
    count = cur.fetchone()["count"]
    conn.close()
    return count

def get_total_instructors():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM instructors;")
    count = cur.fetchone()["count"]
    conn.close()
    return count

def get_total_camps():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM camps;")
    count = cur.fetchone()["count"]
    conn.close()
    return count

def get_total_enrollments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM camp_enrollments;")
    count = cur.fetchone()["count"]
    conn.close()
    return count

def get_upcoming_camps():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.camp_name, c.start_date, c.end_date, c.capacity,
               i.first_name AS instructor_first, i.last_name AS instructor_last
        FROM camps c
        LEFT JOIN instructors i ON c.instructor_id = i.id
        WHERE c.start_date >= CURRENT_DATE
        ORDER BY c.start_date
        LIMIT 10;
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

st.title("Camp Management Dashboard")
st.markdown("Welcome to the dashboard. Here is a quick overview of your camp program.")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total Campers", get_total_campers())
with col2: st.metric("Total Instructors", get_total_instructors())
with col3: st.metric("Total Camps", get_total_camps())
with col4: st.metric("Total Enrollments", get_total_enrollments())

st.markdown("---")

st.subheader("Upcoming Camps")
upcoming = get_upcoming_camps()

if upcoming:
    st.table(upcoming)
else:
    st.info("No upcoming camps found.")
