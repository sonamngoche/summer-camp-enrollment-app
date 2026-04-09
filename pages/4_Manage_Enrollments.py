import streamlit as st
import psycopg2
import psycopg2.extras

st.set_page_config(page_title="Manage Enrollments", layout="wide")

def get_connection():
    return psycopg2.connect(
        st.secrets["DB_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor
    )

# -----------------------------
# LOAD CAMPS
# -----------------------------
def get_camps():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, camp_name
        FROM camps
        ORDER BY start_date;
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# -----------------------------
# LOAD CAMPERS
# -----------------------------
def get_campers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, first_name || ' ' || last_name AS full_name
        FROM campers
        ORDER BY last_name;
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# -----------------------------
# CHECK DUPLICATE ENROLLMENT
# -----------------------------
def check_duplicate(camper_id, camp_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM camp_enrollments
        WHERE camper_id=%s AND camp_id=%s;
    """, (camper_id, camp_id))
    exists = cur.fetchone()
    conn.close()
    return exists is not None

# -----------------------------
# ADD ENROLLMENT
# -----------------------------
def add_enrollment(camper_id, camp_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO camp_enrollments (camper_id, camp_id)
        VALUES (%s, %s);
    """, (camper_id, camp_id))
    conn.commit()
    conn.close()

# -----------------------------
# REMOVE ENROLLMENT
# -----------------------------
def remove_enrollment(enrollment_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM camp_enrollments WHERE id=%s", (enrollment_id,))
    conn.commit()
    conn.close()

# -----------------------------
# PAGE UI
# -----------------------------
st.title("Manage Enrollments")

# Load camps
camps = get_camps()

if not camps:
    st.warning("No camps found. Please add camps first.")
    st.stop()

camp_options = {camp["camp_name"]: camp["id"] for camp in camps}

selected_camp_name = st.selectbox("Select a Camp", list(camp_options.keys()))
selected_camp_id = camp_options[selected_camp_name]

# Load campers
campers = get_campers()

if not campers:
    st.warning("No campers found. Please add campers first.")
    st.stop()

camper_options = {c["full_name"]: c["id"] for c in campers}

st.subheader("Enroll a Camper")

with st.form("enroll_form"):
    camper_name = st.selectbox("Select Camper", list(camper_options.keys()))
    camper_id = camper_options[camper_name]

    submitted = st.form_submit_button("Enroll Camper")

    if submitted:
        if check_duplicate(camper_id, selected_camp_id):
            st.error("This camper is already enrolled in this camp.")
        else:
            add_enrollment(camper_id, selected_camp_id)
            st.success("Camper enrolled successfully!")
            st.experimental_rerun()

# -----------------------------
# SHOW CURRENT ENROLLMENTS
# -----------------------------
st.subheader("Current Enrollments")

conn = get_connection()
cur = conn.cursor()
cur.execute("""
    SELECT ce.id AS enrollment_id,
           c.first_name || ' ' || c.last_name AS camper_name,
           c.age,
           c.guardian_email
    FROM camp_enrollments ce
    JOIN campers c ON ce.camper_id = c.id
    WHERE ce.camp_id=%s
    ORDER BY c.last_name;
""", (selected_camp_id,))
enrollments = cur.fetchall()
conn.close()

if enrollments:
    for e in enrollments:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{e['camper_name']}** — Age {e['age']}")
            st.write(f"Guardian Email: {e['guardian_email']}")
        with col2:
            if st.button("Remove", key=f"remove_{e['enrollment_id']}"):
                remove_enrollment(e["enrollment_id"])
                st.success("Enrollment removed.")
                st.experimental_rerun()
else:
    st.info("No campers enrolled in this camp yet.")
