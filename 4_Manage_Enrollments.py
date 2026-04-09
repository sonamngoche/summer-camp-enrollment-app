import streamlit as st
import psycopg2
import psycopg2.extras

st.set_page_config(page_title="Manage Enrollments", layout="wide")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"], cursor_factory=psycopg2.extras.RealDictCursor)

def get_camps():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, camp_name, start_date, end_date, capacity, description
        FROM camps
        ORDER BY start_date;
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_camp_details(camp_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, camp_name, description, start_date, end_date, capacity
        FROM camps
        WHERE id = %s;
    """, (camp_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_enrolled_campers(camp_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ce.id AS enrollment_id,
               c.id AS camper_id,
               c.first_name,
               c.last_name,
               c.age,
               c.guardian_email
        FROM camp_enrollments ce
        JOIN campers c ON ce.camper_id = c.id
        WHERE ce.camp_id = %s
        ORDER BY c.last_name;
    """, (camp_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_campers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, first_name, last_name
        FROM campers
        ORDER BY last_name;
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def check_duplicate_enrollment(camper_id, camp_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM camp_enrollments
        WHERE camper_id = %s AND camp_id = %s;
    """, (camper_id, camp_id))
    exists = cur.fetchone()
    conn.close()
    return exists is not None

def add_enrollment(camper_id, camp_id):
    conn = get_connection()
