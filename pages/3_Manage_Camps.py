import streamlit as st
import psycopg2
from psycopg2 import sql
from datetime import date

def get_db_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

def validate_camp_data(camp_name, instructor_id, start_date, end_date, capacity):
    if not camp_name:
        return "Camp name cannot be blank."
    if instructor_id is None:
        return "Instructor is required."
    if start_date >= end_date:
        return "Start date must be before end date."
    if not isinstance(capacity, int) or capacity <= 0:
        return "Capacity must be a positive integer."
    return None

st.title("Camps Management")

# -----------------------------
# ADD CAMP FORM
# -----------------------------
with st.form("add_camp_form"):
    st.header("Add Camp")
    camp_name = st.text_input("Camp Name")
    description = st.text_area("Description")

    # Load instructors
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, first_name || ' ' || last_name AS full_name
                FROM instructors
                ORDER BY last_name;
            """)
            instructors = cur.fetchall()

    if not instructors:
        st.warning("No instructors found. Please add instructors first.")
        st.form_submit_button("Add Camp", disabled=True)
        submitted = False
    else:
        instructor_options = {name: id for id, name in instructors}
        instructor_label = st.selectbox("Instructor", list(instructor_options.keys()))
        instructor_id = instructor_options[instructor_label]

        start_date = st.date_input("Start Date", min_value=date.today())
        end_date = st.date_input("End Date", min_value=start_date)
        capacity = st.number_input("Capacity", min_value=1, step=1)

        submitted = st.form_submit_button("Add Camp")

    if submitted:
        error = validate_camp_data(camp_name, instructor_id, start_date, end_date, capacity)
        if error:
            st.error(error)
        else:
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO camps (camp_name, description, instructor_id, start_date, end_date, capacity)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (camp_name, description, instructor_id, start_date, end_date, capacity))
                        conn.commit()
                st.success("Camp added successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error adding camp: {e}")

# -----------------------------
# DISPLAY CAMPS
# -----------------------------
st.header("Current Camps")

with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT camps.id, camp_name, description, instructors.first_name, instructors.last_name,
                   start_date, end_date, capacity
            FROM camps
            LEFT JOIN instructors ON camps.instructor_id = instructors.id
            ORDER BY start_date;
        """)
        camps = cur.fetchall()

if camps:
    for camp in camps:
        camp_id, camp_name, description, inst_first, inst_last, start_date, end_date, capacity = camp
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**{camp_name}** — {inst_first or ''} {inst_last or ''}")
            st.write(description or "No description")
            st.write(f"**Dates:** {start_date} → {end_date} | **Capacity:** {capacity}")

        with col2:
            if st.button("Edit", key=f"edit_{camp_id}"):
                st.session_state["edit_camp_id"] = camp_id

            if st.button("Delete", key=f"delete_{camp_id}"):
                st.session_state["delete_camp_id"] = camp_id
else:
    st.info("No camps found.")

# -----------------------------
# EDIT CAMP FORM
# -----------------------------
if "edit_camp_id" in st.session_state:
    camp_id = st.session_state["edit_camp_id"]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT camp_name, description, instructor_id, start_date, end_date, capacity
                FROM camps WHERE id=%s
            """, (camp_id,))
            camp = cur.fetchone()

    if camp:
        camp_name, description, instructor_id, start_date, end_date, capacity = camp

        st.subheader("Edit Camp")

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, first_name || ' ' || last_name AS full_name
                    FROM instructors
                    ORDER BY last_name;
                """)
                instructors = cur.fetchall()

        instructor_options = {name: id for id, name in instructors}
        current_instructor_name = [name for name, id in instructor_options.items() if id == instructor_id][0]

        with st.form("edit_camp_form"):
            edited_name = st.text_input("Camp Name", value=camp_name)
            edited_desc = st.text_area("Description", value=description)

            instructor_label = st.selectbox(
                "Instructor",
                list(instructor_options.keys()),
                index=list(instructor_options.keys()).index(current_instructor_name)
            )
            edited_instructor_id = instructor_options[instructor_label]

            edited_start = st.date_input("Start Date", value=start_date)
            edited_end = st.date_input("End Date", value=end_date)
            edited_capacity = st.number_input("Capacity", min_value=1, value=capacity)

            if st.form_submit_button("Update Camp"):
                error = validate_camp_data(edited_name, edited_instructor_id, edited_start, edited_end, edited_capacity)
                if error:
                    st.error(error)
                else:
                    try:
                        with get_db_connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE camps
                                    SET camp_name=%s, description=%s, instructor_id=%s,
                                        start_date=%s, end_date=%s, capacity=%s
                                    WHERE id=%s
                                """, (edited_name, edited_desc, edited_instructor_id,
                                      edited_start, edited_end, edited_capacity, camp_id))
                                conn.commit()
                        st.success("Camp updated successfully!")
                        del st.session_state["edit_camp_id"]
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error updating camp: {e}")

# -----------------------------
# DELETE CONFIRMATION
# -----------------------------
if "delete_camp_id" in st.session_state:
    camp_id = st.session_state["delete_camp_id"]

    st.warning("Are you sure you want to delete this camp? This action cannot be undone.")

    colA, colB = st.columns(2)

    if colA.button("Yes, delete camp"):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM camps WHERE id=%s", (camp_id,))
                    conn.commit()
            st.success("Camp deleted successfully!")
            del st.session_state["delete_camp_id"]
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error deleting camp: {e}")

    if colB.button("Cancel"):
        del st.session_state["delete_camp_id"]
        st.info("Deletion canceled.")
