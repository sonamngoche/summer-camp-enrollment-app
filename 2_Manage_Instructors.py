import streamlit as st
import psycopg2
import re
from psycopg2 import sql

def get_db_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

def validate_instructor_data(first_name, last_name, email, phone):
    if not first_name or not last_name:
        return "First name and last name cannot be blank."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid email format."
    if phone and not phone.isdigit():
        return "Phone must contain digits only."
    return None

st.title("Instructors Management")

with st.form("add_instructor_form"):
    st.header("Add Instructor")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone", max_chars=20)
    submitted = st.form_submit_button("Add Instructor")

    if submitted:
        error = validate_instructor_data(first_name, last_name, email, phone)
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
            except psycopg2.errors.UniqueViolation:
                st.error("Error: Email already exists.")
            except Exception as e:
                st.error(f"Error adding instructor: {e}")

st.header("Current Instructors")

with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM instructors ORDER BY last_name")
        instructors = cur.fetchall()

if instructors:
    for instructor in instructors:
        instructor_id, first_name, last_name, email, phone, created_at = instructor
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"{first_name} {last_name}, Email: {email}, Phone: {phone}")

        with col2:
            if st.button("Edit", key=f"edit_{instructor_id}"):
                with st.form(f"edit_instructor_form_{instructor_id}", clear_on_submit=True):
                    st.subheader("Edit Instructor")
                    edited_first = st.text_input("First Name", value=first_name)
                    edited_last = st.text_input("Last Name", value=last_name)
                    edited_email = st.text_input("Email", value=email)
                    edited_phone = st.text_input("Phone", value=phone)

                    if st.form_submit_button("Update Instructor"):
                        error = validate_instructor_data(edited_first, edited_last, edited_email, edited_phone)
                        if error:
                            st.error(error)
                        else:
                            try:
                                with get_db_connection() as conn:
                                    with conn.cursor() as cur:
                                        cur.execute("""
                                            UPDATE instructors
                                            SET first_name=%s, last_name=%s, email=%s, phone=%s
                                            WHERE id=%s
                                        """, (edited_first, edited_last, edited_email, edited_phone, instructor_id))
                                        conn.commit()
                                st.success("Instructor updated successfully!")
                            except psycopg2.errors.UniqueViolation:
                                st.error("Error: Email already exists.")
                            except Exception as e:
                                st.error(f"Error updating instructor: {e}")

            if st.button("Delete", key=f"delete_{instructor_id}"):
                if st.confirm("Are you sure you want to delete this instructor?"):
                    try:
                        with get_db_connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM instructors WHERE id=%s", (instructor_id,))
                                conn.commit()
                        st.success("Instructor deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting instructor: {e}")
else:
    st.info("No instructors found.")
