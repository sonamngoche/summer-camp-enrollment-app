import streamlit as st
import psycopg2
import re

def validate_instructor(first_name, last_name, email, phone):
    if not first_name or not last_name:
        return "First and last name are required."
    if "@" not in email:
        return "Invalid email format."
    if phone and not phone.isdigit():
        return "Phone number must contain digits only."
    return None
    
def get_db_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("Instructors Management")
with st.form("add_instructor_form"):
    st.header("Add Instructor")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")

    submitted = st.form_submit_button("Add Instructor")

    if submitted:
        # CALL THE VALIDATION FUNCTION HERE
        error = validate_instructor(first_name, last_name, email, phone)

        if error:
            st.error(error)
        else:
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO instructors (first_name, last_name, email, phone)
                            VALUES (%s, %s, %s, %s)
                        """, (first_name, last_name, email, phone))
                        conn.commit()
                st.success("Instructor added successfully!")
            except Exception as e:
                st.error(f"Error adding instructor: {e}")

# -----------------------------
# DISPLAY INSTRUCTORS
# -----------------------------
st.header("Current Instructors")

with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, first_name, last_name, email, phone FROM instructors ORDER BY last_name")
        instructors = cur.fetchall()

if instructors:
    for instructor in instructors:
        instructor_id, first_name, last_name, email, phone = instructor

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"{first_name} {last_name} — {email} — {phone}")

        with col2:
            # EDIT BUTTON (if you add edit later)
            if st.button("Edit", key=f"edit_{instructor_id}"):
                st.session_state["edit_instructor_id"] = instructor_id

            # DELETE BUTTON
            if st.button("Delete", key=f"delete_{instructor_id}"):
                st.session_state["delete_instructor_id"] = instructor_id

# -----------------------------
# DELETE CONFIRMATION
# -----------------------------
if "delete_instructor_id" in st.session_state:
    instructor_id = st.session_state["delete_instructor_id"]

    st.warning("Are you sure you want to delete this instructor? This action cannot be undone.")

    colA, colB = st.columns(2)

    if colA.button("Yes, delete instructor"):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM instructors WHERE id=%s", (instructor_id,))
                    conn.commit()
            st.success("Instructor deleted successfully!")
            del st.session_state["delete_instructor_id"]
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error deleting instructor: {e}")

    if colB.button("Cancel"):
        del st.session_state["delete_instructor_id"]
        st.info("Deletion canceled.")
