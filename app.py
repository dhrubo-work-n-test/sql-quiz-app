import streamlit as st
import sqlite3
import pandas as pd
import time

st.set_page_config(page_title="SQL Practice Game", page_icon="🧠", layout="wide")

# -----------------------------
# DATABASE SETUP
# -----------------------------
@st.cache_resource
def init_db():
    conn = sqlite3.connect("sql_practice.db", check_same_thread=False)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT,
        marks INTEGER
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT,
        instructor TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Enrollments (
        enroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        grade TEXT,
        FOREIGN KEY(student_id) REFERENCES Students(student_id),
        FOREIGN KEY(course_id) REFERENCES Courses(course_id)
    );
    """)

    # Insert demo data if empty
    cursor.execute("SELECT COUNT(*) FROM Students;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO Students (name, city, marks) VALUES (?, ?, ?)", [
            ('Amit', 'Delhi', 90),
            ('Riya', 'Mumbai', 85),
            ('Karan', 'Pune', 78),
            ('Sneha', 'Delhi', 92),
            ('Tina', 'Mumbai', 70),
            ('Rahul', 'Chennai', 88),
            ('Rohit', 'Pune', 75)
        ])

        cursor.executemany("INSERT INTO Courses (course_name, instructor) VALUES (?, ?)", [
            ('SQL Basics', 'Anita'),
            ('Data Science', 'Ravi'),
            ('Python', 'Meena')
        ])

        cursor.executemany("INSERT INTO Enrollments (student_id, course_id, grade) VALUES (?, ?, ?)", [
            (1, 1, 'A'),
            (2, 2, 'B'),
            (3, 3, 'A'),
            (4, 1, 'A'),
            (5, 2, 'C'),
            (6, 3, 'B')
        ])
        conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# -----------------------------
# QUESTION BANK
# -----------------------------
QUESTIONS = {
    "Easy": [
        ("Show all student names and their cities", "SELECT name, city FROM Students;"),
        ("Show all students who live in Delhi", "SELECT * FROM Students WHERE city = 'Delhi';"),
        ("List students whose marks are greater than 80", "SELECT name, marks FROM Students WHERE marks > 80;"),
        ("Find students whose city starts with 'M'", "SELECT * FROM Students WHERE city LIKE 'M%';"),
        ("Find total number of students", "SELECT COUNT(*) AS total_students FROM Students;"),
    ],
    "Advanced": [
        ("Find cities where average marks are above 80", "SELECT city, AVG(marks) AS avg_marks FROM Students GROUP BY city HAVING AVG(marks) > 80;"),
        ("Show all students with the courses they enrolled in", "SELECT s.name, c.course_name, e.grade FROM Students s JOIN Enrollments e ON s.student_id = e.student_id JOIN Courses c ON c.course_id = e.course_id;"),
        ("Find students who have not enrolled in any course", "SELECT s.name FROM Students s LEFT JOIN Enrollments e ON s.student_id = e.student_id WHERE e.enroll_id IS NULL;"),
        ("List students with marks greater than average marks", "SELECT name, marks FROM Students WHERE marks > (SELECT AVG(marks) FROM Students);"),
        ("Find city with highest number of students", "SELECT city, COUNT(*) AS total FROM Students GROUP BY city ORDER BY total DESC LIMIT 1;"),
    ],
    "Mock": [
        ("List all students whose marks are more than 75", "SELECT * FROM Students WHERE marks > 75;"),
        ("Find how many students are from each city", "SELECT city, COUNT(*) AS total_students FROM Students GROUP BY city;"),
        ("Display students whose city name ends with 'i'", "SELECT * FROM Students WHERE city LIKE '%i';"),
        ("Find highest and lowest marks", "SELECT MAX(marks), MIN(marks) FROM Students;"),
        ("Show all cities where average marks exceed 85", "SELECT city, AVG(marks) FROM Students GROUP BY city HAVING AVG(marks) > 85;"),
    ]
}

# -----------------------------
# FUNCTION: Timed Answer Display
# -----------------------------
def timed_answer(question_text, answer_sql, key):
    st.write(f"#### ❓ {question_text}")
    col1, col2 = st.columns([2, 1])
    user_query = col1.text_area("💻 Write your SQL query here:", key=f"query_{key}", height=100)
    run = col1.button("▶️ Run Query", key=f"run_{key}")

    # Answer Button
    show_ans = col2.button("💡 Show Answer", key=f"ans_{key}")

    if show_ans:
        st.session_state[key] = True
        st.session_state[f"{key}_time"] = time.time()

    if st.session_state.get(key):
        placeholder = st.empty()
        with placeholder:
            st.code(answer_sql, language="sql")
        elapsed = time.time() - st.session_state[f"{key}_time"]
        if elapsed > 15:
            placeholder.empty()
            st.session_state[key] = False

    # Run query
    if run:
        try:
            result = pd.read_sql_query(user_query, conn)
            st.success("✅ Query executed successfully!")
            st.dataframe(result)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# -----------------------------
# PAGE CONTENT
# -----------------------------
st.title("🧠 SQL Practice & Mock Test Game")
st.markdown("Write SQL queries, check results, and reveal correct answers (visible for 15 seconds).")

# Dropdown for mode selection
mode = st.selectbox("Select Difficulty Level", ["Easy", "Advanced", "Mock"])

# Display Tables
st.subheader("📋 Reference Tables")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Students Table")
    st.dataframe(pd.read_sql_query("SELECT * FROM Students;", conn))
with col2:
    st.caption("Courses Table")
    st.dataframe(pd.read_sql_query("SELECT * FROM Courses;", conn))
with col3:
    st.caption("Enrollments Table")
    st.dataframe(pd.read_sql_query("SELECT * FROM Enrollments;", conn))

st.divider()

# Display selected questions
st.header(f"🏁 {mode} Level Questions")
for i, (q, ans) in enumerate(QUESTIONS[mode], start=1):
    timed_answer(q, ans, f"{mode}_{i}")
    st.divider()
