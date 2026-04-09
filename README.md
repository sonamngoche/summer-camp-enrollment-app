# summer-camp-enrollment-app
streamlit based summer camp management system w postgresql backend
This system tracks registration for summer camp, specifically documenting who signs up for which camp along with all the relevant information. This system would be used by administrative staff at summer camp to manage all data related to enrollment and contact information.

campers — id (SERIAL PK), first_name (VARCHAR 100, NOT NULL), last_name (VARCHAR 100, NOT NULL), age (INTEGER NOT NULL), guardian_email (VARCHAR 150, NOT NULL), guardian_phone (VARCHAR 20), created_at (TIMESTAMP, DEFAULT NOW)
instructors — id (SERIAL PK), first_name (VARCHAR 100, NOT NULL), last_name (VARCHAR 100, NOT NULL), email (VARCHAR 150, UNIQUE, NOT NULL), phone (VARCHAR 20), created_at (TIMESTAMP, DEFAULT NOW)

camps — id (SERIAL PK), camp_name (VARCHAR 150, NOT NULL), description (TEXT), instructor_id (INTEGER FK → instructors.id ON DELETE SET NULL), start_date (DATE NOT NULL), end_date (DATE NOT NULL), capacity (INTEGER NOT NULL), created_at (TIMESTAMP, DEFAULT NOW)
camp_enrollments — id (SERIAL PK), camper_id (INTEGER FK → campers.id ON DELETE CASCADE), camp_id (INTEGER FK → camps.id ON DELETE CASCADE), enrolled_at (TIMESTAMP, DEFAULT NOW), UNIQUE(camper_id, camp_id)

- One instructor teaches many camps (one‑to‑many).
- One camp has many campers through enrollments (one‑to‑many from camps → camp_enrollments).
- One camper can enroll in many camps (one‑to‑many from campers → camp_enrollments).
- Campers connect to camps through camp_enrollments (many‑to‑many: one camper can join multiple camps, and each camp can have multiple campers).


Home Page — Shows summary metrics: total campers, total instructors, total camps, and total enrollments. Displays a table of upcoming camps sorted by start date.
Manage Campers — Form to add a new camper (first name, last name, age, guardian email, guardian phone). Table below showing all campers with Edit and Delete buttons. Edit opens a form pre‑filled with current values. Delete asks for confirmation.
Manage Instructors — Form to add a new instructor (first name, last name, email, phone). Table showing all instructors with Edit and Delete options. Edit loads a pre‑filled form; Delete requires confirmation.
Manage Camps — Form to add a new camp (camp name, description, instructor dropdown, start date, end date, capacity). Table showing all camps with Edit and Delete buttons. Edit opens a pre‑filled form; Delete requires confirmation.
Manage Enrollments — Dropdown to select a camp. Shows camp details and a roster of enrolled campers. Form to add a camper to the selected camp (camper dropdown). Each roster row includes a Remove button to delete an enrollment with confirmation.
Search / Filter Page — Allows users to search campers by last name or filter camps by date range. Displays matching results in a table.

• 	Camper first name: cannot be blank
• 	Camper last name: cannot be blank
• 	Camper age: must be a positive integer
• 	Guardian email: must match standard email regex pattern
• 	Guardian phone: digits only if provided
• 	Instructor first name: cannot be blank
• 	Instructor last name: cannot be blank
• 	Instructor email: must match email regex pattern
• 	Instructor phone: digits only if provided
• 	Camp name: cannot be blank
• 	Instructor selection: required

• 	Start and end dates: start_date must be before end_date
• 	Capacity: must be a positive integer
• 	Enrollment: camper and camp selections cannot be blank

#linktostreamlit
https://summer-camp-enrollment-app-f5wkqmexwzpccmdgf5hrde.streamlit.app/
• 	Enrollment: prevent duplicate enrollments

 
