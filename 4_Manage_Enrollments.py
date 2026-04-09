import streamlit as st
import psycopg2
import psycopg2.extras

st.set_page_config(page_title="Manage Enrollments", layout="wide")

# -----------------------------
# Database Connection
# -----------------------------
def get_connection():
    return psycopg2.connect(
        st.secrets["DB_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor
    )

# -----------------------------
# Validation
# -----------------------------
def validate_enrollment(camper_id, camp_id):
    if not camper_id:
        return "You must select a camper."
    if not camp_id:
        return "You must select a camp."
    return None

# -----------------------------
# Query Helpers
# -----------------------------
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
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO camp_enrollments (camper_id, camp_id)
        VALUES (%s, %s);
    """, (camper_id, camp_id))
    conn.commit()
    conn.close()

def delete_enrollment(enrollment_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM camp_enrollments WHERE id = %s;", (enrollment_id,))
    conn.commit()
    conn.close()

# -----------------------------
# Page UI
# -----------------------------
st.title("Manage Enrollments")

# Load camps
camps = get_camps()
camp_names = {camp["camp_name"]: camp["id"] for camp in camps}

selected_camp_name = st.selectbox("Select a Camp", list(camp_names.keys()))
selected_camp_id = camp_names[selected_camp_name]

# Display camp details
camp_details = get_camp_details(selected_camp_id)
st.subheader(f"{camp_details['camp_name']}")
st.write(camp_details["description"] or "No description provided.")
st.write(f"**Dates:** {camp_details['start_date']} → {camp_details['end_date']}")
st.write(f"**Capacity:** {camp_details['capacity']}")

# Load enrolled campers
enrolled = get_enrolled_campers(selected_camp_id)
current_count = len(enrolled)

st.write(f"**Currently Enrolled:** {current_count} / {camp_details['capacity']}")

# -----------------------------
# Enrollment Form
# -----------------------------
st.subheader("Add Enrollment")

campers = get_all_campers()
camper_options = {f"{c['first_name']} {c['last_name']}": c["id"] for c in campers}

selected_camper_label = st.selectbox("Select Camper", list(camper_options.keys()))
selected_camper_id = camper_options[selected_camper_label]

if st.button("Enroll Camper"):
    # VALIDATION
    error = validate_enrollment(selected_camper_id, selected_camp_id)
    if error:
        st.error(error)
    elif check_duplicate_enrollment(selected_camper_id, selected_camp_id):
        st.error("This camper is already enrolled in this camp.")
    elif current_count >= camp_details["capacity"]:
        st.error("This camp is already at full capacity.")
    else:
        add_enrollment(selected_camper_id, selected_camp_id)
        st.success("Camper enrolled successfully!")
        st.experimental_rerun()

# -----------------------------
# Roster Table
# -----------------------------
st.subheader("Enrolled Campers")

for camper in enrolled:
    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(f"{camper['first_name']} {camper['last_name']} — Age {camper['age']} — {camper['guardian_email']}")

    with col2:
        if st.button("Remove", key=f"remove_{camper['enrollment_id']}"):
            st.session_state["delete_enrollment_id"] = camper["enrollment_id"]

# -----------------------------
# DELETE CONFIRMATION
# -----------------------------
if "delete_enrollment_id" in st.session_state:
    enrollment_id = st.session_state["delete_enrollment_id"]

    st.warning("Are you sure you want to remove this camper from the camp?")

    colA, colB = st.columns(2)

    if colA.button("Yes, remove"):
        delete_enrollment(enrollment_id)
        del st.session_state["delete_enrollment_id"]
        st.success("Enrollment removed successfully!")
        st.experimental_rerun()

    if colB.button("Cancel"):
        del st.session_state["delete_enrollment_id"]
        st.info("Removal canceled.")
