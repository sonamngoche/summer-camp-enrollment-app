import streamlit as st
import psycopg2
import psycopg2.extras
from datetime import date

# -----------------------------
# 1. Database connection function
# -----------------------------
def get_connection():
    return psycopg2.connect(
        st.secrets["DB_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor
    )

# -----------------------------
# 2. Initialize DB (tables)
# -----------------------------
def initialize_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS campers (
            id SERIAL PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            age INT,
            guardian_name TEXT,
            guardian_phone TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS instructors (
            id SERIAL PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            specialty TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS camps (
            id SERIAL PRIMARY KEY,
            camp_name TEXT,
            description TEXT,
            start_date DATE,
            end_date DATE,
            capacity INT,
            instructor_id INT REFERENCES instructors(id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS camp_enrollments (
            id SERIAL PRIMARY KEY,
            camper_id INT REFERENCES campers(id),
            camp_id INT REFERENCES camps(id),
            UNIQUE(camper_id, camp_id)
        );
    """)

    conn.commit()
    conn.close()

# Call AFTER get_connection is defined
initialize_db()

# -----------------------------
# 3. Streamlit page config
# -----------------------------
st.set_page_config(page_title="Camp Dashboard", layout="wide")

# -----------------------------
# 4. Dashboard helper functions
# -----------------------------
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

# -----------------------------
# 5. Dashboard UI
# -----------------------------
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
