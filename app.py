import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="SQL Practice & Mock Test", layout="wide")

st.title("🧩 SQL Practice & Mock Test – Easy to Advanced")
st.write("Test your SQL skills! Choose difficulty, answer queries, and check results. "
         "After 4 wrong attempts, the correct answer will appear.")

# --------------------- DATABASE SETUP --------------------- #
@st.cache_resource
def create_sample_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE Students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT,
        marks INT,
        age INT
    );

    CREATE TABLE Courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT,
        instructor TEXT
    );

    CREATE TABLE Enrollments (
        enroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INT,
        course_id INT,
        grade CHAR(1),
        FOREIGN KEY(student_id) REFERENCES Students(student_id),
        FOREIGN KEY(course_id) REFERENCES Courses(course_id)
    );

    INSERT INTO Students (name, city, marks, age) VALUES
    ('Riya', 'Delhi', 88, 20),
    ('Aarav', 'Mumbai', 92, 21),
    ('Neha', 'Pune', 70, 19),
    ('Kabir', 'Delhi', 85, 22),
    ('Zara', 'Chennai', 95, 20),
    ('Anaya', 'Pune', NULL, 21),
    ('Rohit', 'Delhi', 60, 23),
    ('Maya', 'Mumbai', 75, 22);

    INSERT INTO Courses (course_name, instructor) VALUES
    ('Math', 'Dr. Mehta'),
    ('Science', 'Prof. Rao'),
    ('English', 'Dr. Singh'),
    ('History', 'Prof. Das');

    INSERT INTO Enrollments (student_id, course_id, grade) VALUES
    (1, 1, 'A'),
    (2, 1, 'B'),
    (3, 2, 'C'),
    (4, 3, 'A'),
    (5, 2, 'A'),
    (6, 3, 'B'),
    (7, 4, 'C'),
    (8, 1, 'B');
    """)
    conn.commit()
    return conn


conn = create_sample_db()
# --------------------- SHOW DATABASE TABLES --------------------- #
with st.expander("📋 View Database Tables (click to expand)"):
    st.write("Here are the current tables you can query from:")

    try:
        students_df = pd.read_sql_query("SELECT * FROM Students;", conn)
        courses_df = pd.read_sql_query("SELECT * FROM Courses;", conn)
        enrollments_df = pd.read_sql_query("SELECT * FROM Enrollments;", conn)

        st.subheader("👩‍🎓 Students")
        st.dataframe(students_df, use_container_width=True)

        st.subheader("📘 Courses")
        st.dataframe(courses_df, use_container_width=True)

        st.subheader("🧾 Enrollments")
        st.dataframe(enrollments_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading tables: {e}")


# --------------------- QUESTION SETS --------------------- #
EASY = {
    "Show all student names and their cities.": "SELECT name, city FROM Students;",
    "Show all students who live in Delhi.": "SELECT * FROM Students WHERE city = 'Delhi';",
    "List students whose marks are greater than 80.": "SELECT name, marks FROM Students WHERE marks > 80;",
    "Find students whose city starts with ‘M’.": "SELECT * FROM Students WHERE city LIKE 'M%';",
    "Find total number of students.": "SELECT COUNT(*) AS total_students FROM Students;",
    "Find average marks of all students.": "SELECT AVG(marks) AS avg_marks FROM Students;",
    "Find maximum and minimum marks.": "SELECT MAX(marks) AS max_marks, MIN(marks) AS min_marks FROM Students;",
    "Find number of students per city.": "SELECT city, COUNT(*) AS total_students FROM Students GROUP BY city;",
    "Find students who are from Delhi and have marks above 80.": "SELECT * FROM Students WHERE city='Delhi' AND marks>80;",
    "Find students who are from either Pune or Mumbai.": "SELECT * FROM Students WHERE city IN ('Pune', 'Mumbai');",
    "Find students who are not from Delhi.": "SELECT * FROM Students WHERE city <> 'Delhi';",
    "Find students with marks between 70 and 90.": "SELECT * FROM Students WHERE marks BETWEEN 70 AND 90;",
    "Get a list of all unique city names and instructor names using UNION.": "SELECT city FROM Students UNION SELECT instructor FROM Courses;"
}

ADVANCED = {
    "Find cities where average marks are above 80.": "SELECT city, AVG(marks) AS avg_marks FROM Students GROUP BY city HAVING AVG(marks) > 80;",
    "Find how many students have NULL marks.": "SELECT COUNT(*) AS null_marks_count FROM Students WHERE marks IS NULL;",
    "Show all students with the courses they enrolled in (using JOIN).": "SELECT s.name, c.course_name, e.grade FROM Students s JOIN Enrollments e ON s.student_id = e.student_id JOIN Courses c ON c.course_id = e.course_id;",
    "Find students who have not enrolled in any course (using LEFT JOIN).": "SELECT s.name FROM Students s LEFT JOIN Enrollments e ON s.student_id = e.student_id WHERE e.enroll_id IS NULL;",
    "Find all distinct names (student + instructor) who are from Delhi or teach a subject (using UNION).": "SELECT name FROM Students WHERE city='Delhi' UNION SELECT instructor FROM Courses;",
    "Find total count of all people in both Students and Courses tables combined (using UNION ALL).": "SELECT COUNT(*) FROM (SELECT name FROM Students UNION ALL SELECT instructor FROM Courses) AS all_people;",
    "List students with marks greater than the average marks of all students.": "SELECT name, marks FROM Students WHERE marks > (SELECT AVG(marks) FROM Students);",
    "Find the city with the highest number of students.": "SELECT city, COUNT(*) AS total FROM Students GROUP BY city ORDER BY total DESC LIMIT 1;",
    "Find the student(s) who have the highest marks in each city.": "SELECT s1.name, s1.city, s1.marks FROM Students s1 WHERE marks = (SELECT MAX(s2.marks) FROM Students s2 WHERE s2.city = s1.city);"
}

MOCK = {
    "List all students whose marks are more than 75.": "SELECT * FROM Students WHERE marks > 75;",
    "Find how many students are from each city.": "SELECT city, COUNT(*) AS total_students FROM Students GROUP BY city;",
    "Display students whose city name ends with ‘i’.": "SELECT * FROM Students WHERE city LIKE '%i';",
    "Find the highest and lowest marks among all students.": "SELECT MAX(marks), MIN(marks) FROM Students;",
    "Show all cities where average marks exceed 85.": "SELECT city, AVG(marks) FROM Students GROUP BY city HAVING AVG(marks) > 85;",
    "Find students who are enrolled in more than one course.": "SELECT student_id, COUNT(*) FROM Enrollments GROUP BY student_id HAVING COUNT(*) > 1;",
    "List all students and their respective grades using JOIN.": "SELECT s.name, c.course_name, e.grade FROM Students s JOIN Enrollments e ON s.student_id=e.student_id JOIN Courses c ON c.course_id=e.course_id;",
    "Find the total number of unique instructors and students combined.": "SELECT COUNT(*) FROM (SELECT name FROM Students UNION SELECT instructor FROM Courses) AS all_people;",
    "Show the name and marks of the top-performing student(s).": "SELECT name, marks FROM Students WHERE marks = (SELECT MAX(marks) FROM Students);",
    "Display the count of students with NULL marks.": "SELECT COUNT(*) FROM Students WHERE marks IS NULL;"
}

# --------------------- INTERFACE --------------------- #
category = st.selectbox("Choose difficulty level:", ["Easy", "Advanced", "Mock Test"])

if category == "Easy":
    QUESTIONS = EASY
elif category == "Advanced":
    QUESTIONS = ADVANCED
else:
    QUESTIONS = MOCK

question = st.selectbox("Select a question:", list(QUESTIONS.keys()))

if "attempts" not in st.session_state:
    st.session_state.attempts = {}

st.write(f"### 🧠 Question: {question}")

user_query = st.text_area("✏️ Write your SQL query below:", height=150)
submit = st.button("Run Query")

if submit:
    try:
        df_user = pd.read_sql_query(user_query, conn)
        df_correct = pd.read_sql_query(QUESTIONS[question], conn)

        if df_user.equals(df_correct):
            st.success("✅ Correct Answer!")
            st.dataframe(df_user)
            st.session_state.attempts[question] = 0
        else:
            st.error("❌ Incorrect result. Try again.")
            st.dataframe(df_user)
            st.session_state.attempts[question] = st.session_state.attempts.get(question, 0) + 1

            if st.session_state.attempts[question] >= 4:
                st.warning("💡 You've tried 4 times! Here's the correct answer:")
                st.code(QUESTIONS[question])
                st.dataframe(df_correct)
                st.session_state.attempts[question] = 0

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
