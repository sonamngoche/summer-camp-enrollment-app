import streamlit as st
import psycopg2
import re
from psycopg2 import sql

def get_db_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

def validate_camper_data(first_name, last_name, age, guardian_email, guardian_phone):
    if not first_name or not last_name:
        return "First name and last name cannot be blank."
    if not isinstance(age, int) or age <= 0:
        return "Age must be a positive integer."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", guardian_email):
        return "Invalid email format."
    if guardian_phone and not guardian_phone.isdigit():
        return "Guardian phone must contain digits only."
    return None

st.title("Campers Management")

with st.form("add_camper_form"):
    st.header("Add Camper")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    age = st.number_input("Age", min_value=1, step=1)
    guardian_email = st.text_input("Guardian Email")
    guardian_phone = st.text_input("Guardian Phone", max_chars=20)
    submitted = st.form_submit_button("Add Camper")

    if submitted:
        error_message = validate_camper_data(first_name, last_name, age, guardian_email, guardian_phone)
        if error_message:
            st.error(error_message)
        else:
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO campers (first_name, last_name, age, guardian_email, guardian_phone)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (first_name, last_name, age, guardian_email, guardian_phone))
                        conn.commit()
                st.success("Camper added successfully!")
            except Exception as e:
                st.error(f"Error adding camper: {e}")

st.header("Current Campers")

with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM campers ORDER BY last_name")
        campers = cur.fetchall()

if campers:
    for camper in campers:
        camper_id, first_name, last_name, age, guardian_email, guardian_phone, created_at = camper
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"{first_name} {last_name}, Age: {age}, Email: {guardian_email}, Phone: {guardian_phone}")

        with col2:
            if st.button("Edit", key=f"edit_{camper_id}"):
                with st.form(f"edit_camper_form_{camper_id}", clear_on_submit=True):
                    st.subheader("Edit Camper")
                    edited_first = st.text_input("First Name", value=first_name)
                    edited_last = st.text_input("Last Name", value=last_name)
                    edited_age = st.number_input("Age", min_value=1, value=age)
                    edited_email = st.text_input("Guardian Email", value=guardian_email)
                    edited_phone = st.text_input("Guardian Phone", value=guardian_phone)

                    if st.form_submit_button("Update Camper"):
                        error = validate_camper_data(edited_first, edited_last, edited_age, edited_email, edited_phone)
                        if error:
                            st.error(error)
                        else:
                            try:
                                with get_db_connection() as conn:
                                    with conn.cursor() as cur:
                                        cur.execute("""
                                            UPDATE campers
                                            SET first_name=%s, last_name=%s, age=%s, guardian_email=%s, guardian_phone=%s
                                            WHERE id=%s
                                        """, (edited_first, edited_last, edited_age, edited_email, edited_phone, camper_id))
                                        conn.commit()
                                st.success("Camper updated successfully!")
                            except Exception as e:
                                st.error(f"Error updating camper: {e}")

            if st.button("Delete", key=f"delete_{camper_id}"):
                if st.confirm("Are you sure you want to delete this camper?"):
                    try:
                        with get_db_connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM campers WHERE id=%s", (camper_id,))
                                conn.commit()
                        st.success("Camper deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting camper: {e}")
else:
    st.info("No campers found.")
