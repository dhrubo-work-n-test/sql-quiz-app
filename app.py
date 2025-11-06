# app.py
"""
Streamlit SQL Quiz App (Hackerrank-style)
- Creates a local SQLite DB with sample data
- Presents questions (easy, advanced, mock)
- Lets user submit SELECT queries and checks them against reference answers
"""

import sqlite3
import pandas as pd
import streamlit as st
import sqlparse
from typing import Tuple, List

st.set_page_config(page_title="SQL Quiz — Practice & Test", layout="wide")

# ---------------------------
# Helper: Safety check
# ---------------------------
FORBIDDEN = [
    "INSERT ", "UPDATE ", "DELETE ", "DROP ", "TRUNCATE ", "ALTER ", "CREATE ",
    "ATTACH ", "DETACH ", "PRAGMA ", "REINDEX ", "REPLACE ", "EXECUTE ", "MERGE "
]

def is_select_only(query: str) -> bool:
    q = query.strip().lower()
    # Quick parse: must start with select
    if not q.startswith("select"):
        return False
    # forbid dangerous keywords
    up = query.upper()
    for kw in FORBIDDEN:
        if kw in up:
            return False
    return True

# ---------------------------
# Build sample DB (SQLite)
# ---------------------------
@st.experimental_singleton
def create_sample_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cur = conn.cursor()

    # Create tables (SQLite-friendly)
    cur.executescript("""
    CREATE TABLE Students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT,
        marks INTEGER,
        age INTEGER
    );

    CREATE TABLE Courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT,
        instructor TEXT
    );

    CREATE TABLE Enrollments (
        enroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        grade TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id),
        FOREIGN KEY (course_id) REFERENCES Courses(course_id)
    );
    """)

    # Insert sample data into Students
    students = [
        ('Riya', 'Delhi', 88, 20),
        ('Aarav', 'Mumbai', 92, 21),
        ('Neha', 'Pune', 70, 19),
        ('Kabir', 'Delhi', 85, 22),
        ('Zara', 'Chennai', 95, 20),
        ('Anaya', 'Pune', None, 21),
        ('Rohit', 'Delhi', 60, 23),
        ('Maya', 'Mumbai', 75, 22)
    ]
    cur.executemany("INSERT INTO Students (name, city, marks, age) VALUES (?, ?, ?, ?);", students)

    # Insert into Courses
    courses = [
        ('Math', 'Dr. Mehta'),
        ('Science', 'Prof. Rao'),
        ('English', 'Dr. Singh'),
        ('History', 'Prof. Das')
    ]
    cur.executemany("INSERT INTO Courses (course_name, instructor) VALUES (?, ?);", courses)

    # Insert into Enrollments
    enrolls = [
        (1, 1, 'A'),
        (2, 1, 'B'),
        (3, 2, 'C'),
        (4, 3, 'A'),
        (5, 2, 'A'),
        (6, 3, 'B'),
        (7, 4, 'C'),
        (8, 1, 'B')
    ]
    cur.executemany("INSERT INTO Enrollments (student_id, course_id, grade) VALUES (?, ?, ?);", enrolls)

    conn.commit()
    return conn

conn = create_sample_db()

# ---------------------------
# Questions & Reference Queries (SQLite-adapted)
# ---------------------------
# Each item: (id, title, prompt_text, reference_query, enforce_order)
QUESTIONS = [
    # Easy
    ("E1", "Names & Cities", "Show all student names and their cities.",
     "SELECT name, city FROM Students;", False),

    ("E2", "Students from Delhi", "Show all students who live in Delhi.",
     "SELECT * FROM Students WHERE city = 'Delhi';", False),

    ("E3", "Marks > 80", "List students whose marks are greater than 80.",
     "SELECT name, marks FROM Students WHERE marks > 80;", False),

    ("E4", "City starts with M", "Find students whose city starts with 'M'.",
     "SELECT * FROM Students WHERE city LIKE 'M%';", False),

    ("E5", "Total students", "Find total number of students.",
     "SELECT COUNT(*) AS total_students FROM Students;", False),

    ("E6", "Average marks", "Find average marks of all students.",
     "SELECT AVG(marks) AS avg_marks FROM Students;", False),

    ("E7", "Max & Min marks", "Find maximum and minimum marks.",
     "SELECT MAX(marks) AS max_marks, MIN(marks) AS min_marks FROM Students;", False),

    ("E8", "Students per city", "Find number of students per city.",
     "SELECT city, COUNT(*) AS total_students FROM Students GROUP BY city;", False),

    ("E9", "Delhi AND marks>80", "Find students who are from Delhi and have marks above 80.",
     "SELECT * FROM Students WHERE city='Delhi' AND marks>80;", False),

    ("E10", "Pune or Mumbai", "Find students who are from either Pune or Mumbai.",
     "SELECT * FROM Students WHERE city IN ('Pune', 'Mumbai');", False),

    ("E11", "Not Delhi", "Find students who are not from Delhi.",
     "SELECT * FROM Students WHERE city <> 'Delhi';", False),

    ("E12", "Marks between 70 and 90", "Find students with marks between 70 and 90.",
     "SELECT * FROM Students WHERE marks BETWEEN 70 AND 90;", False),

    ("E13", "UNION cities & instructors", "Get a list of all unique city names and instructor names using UNION.",
     "SELECT city AS name FROM Students UNION SELECT instructor AS name FROM Courses;", False),

    # Advanced
    ("A1", "Cities avg > 80", "Find cities where average marks are above 80.",
     "SELECT city, AVG(marks) AS avg_marks FROM Students GROUP BY city HAVING AVG(marks) > 80;", False),

    ("A2", "NULL marks count", "Find how many students have NULL marks.",
     "SELECT COUNT(*) AS null_marks_count FROM Students WHERE marks IS NULL;", False),

    ("A3", "Students & courses (JOIN)", "Show all students with the courses they enrolled in.",
     "SELECT s.name, c.course_name, e.grade FROM Students s JOIN Enrollments e ON s.student_id = e.student_id JOIN Courses c ON c.course_id = e.course_id;", False),

    ("A4", "Not enrolled (LEFT JOIN)", "Find students who have not enrolled in any course.",
     "SELECT s.name FROM Students s LEFT JOIN Enrollments e ON s.student_id = e.student_id WHERE e.enroll_id IS NULL;", False),

    ("A5", "Distinct names UNION", "Find all distinct names (student + instructor).",
     "SELECT name FROM Students UNION SELECT instructor FROM Courses;", False),

    ("A6", "Count all people", "Find total count of all people in both Students and Courses tables combined.",
     "SELECT COUNT(*) FROM (SELECT name FROM Students UNION ALL SELECT instructor FROM Courses) AS all_people;", False),

    ("A7", "Marks > avg", "List students with marks greater than the average marks of all students.",
     "SELECT name, marks FROM Students WHERE marks > (SELECT AVG(marks) FROM Students);", False),

    ("A8", "City with most students", "Find the city with the highest number of students.",
     "SELECT city, COUNT(*) AS total FROM Students GROUP BY city ORDER BY total DESC LIMIT 1;", False),

    ("A9", "Top per city", "Find the student(s) who have the highest marks in each city.",
     "SELECT s1.name, s1.city, s1.marks FROM Students s1 WHERE marks = (SELECT MAX(s2.marks) FROM Students s2 WHERE s2.city = s1.city);", False),

    # Mock Test (10)
    ("M1", "Marks > 75", "List all students whose marks are more than 75.",
     "SELECT * FROM Students WHERE marks > 75;", False),

    ("M2", "Count per city", "Find how many students are from each city.",
     "SELECT city, COUNT(*) AS total_students FROM Students GROUP BY city;", False),

    ("M3", "City ends with i", "Display students whose city name ends with 'i'.",
     "SELECT * FROM Students WHERE city LIKE '%i';", False),

    ("M4", "Highest & lowest marks", "Find the highest and lowest marks among all students.",
     "SELECT MAX(marks) AS max_mark, MIN(marks) AS min_mark FROM Students;", False),

    ("M5", "Cities avg > 85", "Show all cities where average marks exceed 85.",
     "SELECT city, AVG(marks) FROM Students GROUP BY city HAVING AVG(marks) > 85;", False),

    ("M6", "Enrolled >1 course", "Find students who are enrolled in more than one course.",
     "SELECT student_id, COUNT(*) AS cnt FROM Enrollments GROUP BY student_id HAVING COUNT(*) > 1;", False),

    ("M7", "Students & grades", "List all students and their respective grades using JOIN.",
     "SELECT s.name, c.course_name, e.grade FROM Students s JOIN Enrollments e ON s.student_id=e.student_id JOIN Courses c ON c.course_id=e.course_id;", False),

    ("M8", "Unique people count", "Find the total number of unique instructors and students combined.",
     "SELECT COUNT(*) FROM (SELECT name FROM Students UNION SELECT instructor FROM Courses) AS all_people;", False),

    ("M9", "Top performer", "Show the name and marks of the top-performing student(s).",
     "SELECT name, marks FROM Students WHERE marks = (SELECT MAX(marks) FROM Students);", False),

    ("M10", "Count NULL marks", "Display the count of students with NULL marks.",
     "SELECT COUNT(*) FROM Students WHERE marks IS NULL;", False),
]

# ---------------------------
# Precompute expected results (dataframes)
# ---------------------------
@st.experimental_singleton
def prepare_reference_results():
    c = create_sample_db()
    refs = {}
    for q in QUESTIONS:
        qid = q[0]
        ref_q = q[3]
        try:
            df = pd.read_sql_query(ref_q, c)
        except Exception as e:
            # Store error; but app will show reference query on request
            df = pd.DataFrame({"error": [str(e)]})
        refs[qid] = df
    return refs

REFS = prepare_reference_results()

# ---------------------------
# UI: Sidebar & question selection
# ---------------------------
st.title("🧠 SQL Practice — Interactive (Streamlit Hackerrank-style)")

st.sidebar.header("Select Question")
group = st.sidebar.radio("Question group", ("Easy", "Advanced", "Mock Test"))

# filter questions based on group
if group == "Easy":
    qlist = [q for q in QUESTIONS if q[0].startswith("E")]
elif group == "Advanced":
    qlist = [q for q in QUESTIONS if q[0].startswith("A")]
else:
    qlist = [q for q in QUESTIONS if q[0].startswith("M")]

q_options = {f"{q[0]} - {q[1]}": q for q in qlist}
sel_label = st.sidebar.selectbox("Pick a question", list(q_options.keys()))
qid, qtitle, qprompt, qref, qenforce = q_options[sel_label]

st.header(f"{qid}: {qtitle}")
st.write(qprompt)
st.markdown("---")

# show reference table shape and sample if user wants
with st.expander("Reference result preview (computed from reference query)"):
    st.write("Reference query:")
    st.code(qref)
    try:
        st.write("Reference output (first 10 rows):")
        st.dataframe(REFS[qid].head(10))
    except Exception as e:
        st.write("Error preparing reference:", e)

# Query input
st.subheader("Write your SQL (only SELECT queries allowed)")
default_sql = qref  # prefill with reference for learning
user_sql = st.text_area("Your SQL query", value=default_sql, height=160)

enforce_order = st.checkbox("Enforce order when comparing results (if relevant)", value=False)
show_ref_query = st.checkbox("Show reference query (hint)", value=False)

if show_ref_query:
    st.code(qref)

run = st.button("Run & Check")

# ---------------------------
# Execution & evaluation
# ---------------------------
def run_user_query(conn: sqlite3.Connection, query: str) -> Tuple[pd.DataFrame, str]:
    # validate
    if not is_select_only(query):
        return pd.DataFrame(), "Only single SELECT queries are allowed. No DML/DDL."
    try:
        df = pd.read_sql_query(query, conn)
        return df, ""
    except Exception as e:
        return pd.DataFrame(), f"SQL error: {e}"

def compare_results(df_user: pd.DataFrame, df_ref: pd.DataFrame, enforce_order: bool) -> Tuple[bool, str]:
    # if reference had error, we can't compare
    if "error" in df_ref.columns:
        return False, f"Reference query failed: {df_ref.loc[0,'error']}"
    # normalize NaNs to None for comparison
    uvals = [tuple(None if (pd.isna(x)) else x for x in row) for row in df_user.to_numpy(dtype=object)]
    rvals = [tuple(None if (pd.isna(x)) else x for x in row) for row in df_ref.to_numpy(dtype=object)]
    if enforce_order:
        ok = (uvals == rvals)
    else:
        ok = (set(uvals) == set(rvals))
    # Build helpful diff message
    if ok:
        return True, "Correct — your result matches the reference."
    else:
        # compute missing/extra
        extra = [r for r in uvals if r not in rvals]
        missing = [r for r in rvals if r not in uvals]
        msg = ""
        if extra:
            msg += f"Rows in your result but NOT expected (examples up to 5): {extra[:5]}\n"
        if missing:
            msg += f"Rows expected but NOT in your result (examples up to 5): {missing[:5]}\n"
        if not msg:
            msg = "Result differs from expected (may be ordering or formatting)."
        return False, msg

if run:
    conn = conn  # from create_sample_db singleton
    df_user, err = run_user_query(conn, user_sql)
    if err:
        st.error(err)
    else:
        st.subheader("Your query result (first 20 rows)")
        st.dataframe(df_user.head(20))
        st.write(f"Rows returned: {len(df_user)}")
        # compare to reference
        df_ref = REFS[qid]
        correct, msg = compare_results(df_user, df_ref, enforce_order)
        if correct:
            st.success(msg)
        else:
            st.error(msg)
            with st.expander("Reference full result"):
                st.dataframe(df_ref)
            # show short guidance
            st.markdown("**Hints:**")
            st.markdown("- Check column order and names (the reference columns must match).")
            st.markdown("- Check `WHERE` conditions and `GROUP BY`/`HAVING` logic.")
            st.markdown("- Use `ORDER BY` if the question expects a certain order and you checked 'Enforce order'.")
            st.markdown("- If your DB dialect differs (Postgres vs SQLite), adjust functions (`RIGHT` -> `SUBSTR(..., -3)`, `ILIKE` -> `LOWER(...) LIKE`).")

st.markdown("---")
st.caption("This app runs a local SQLite DB and compares results. For a production / multi-user platform you would use a server database, user auth, and stronger sandboxing.")
