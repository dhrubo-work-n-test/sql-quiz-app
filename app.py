import streamlit as st
import sqlite3
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="SQL Practice Game 🎯", page_icon="💾", layout="centered")

st.title("🎯 SQL Practice Game")
st.write("Learn and test your SQL skills interactively, just like HackerRank! 🚀")

# --- DATABASE CREATION ---
@st.cache_resource
def create_sample_db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    # Employee Table
    cur.execute("""
    CREATE TABLE Employee (
        ID INTEGER PRIMARY KEY,
        Name TEXT,
        Age INTEGER,
        Department TEXT,
        Salary INTEGER,
        Months INTEGER
    );
    """)

    employees = [
        (1, "Amit", 28, "HR", 50000, 12),
        (2, "Riya", 31, "Finance", 65000, 10),
        (3, "John", 25, "Tech", 72000, 8),
        (4, "Sara", 35, "Tech", 80000, 15),
        (5, "Tom", 27, "HR", 49000, 11),
    ]
    cur.executemany("INSERT INTO Employee VALUES (?, ?, ?, ?, ?, ?);", employees)

    # Station Table
    cur.execute("""
    CREATE TABLE Station (
        ID INTEGER PRIMARY KEY,
        City TEXT,
        State TEXT,
        Population INTEGER
    );
    """)
    stations = [
        (1, "Delhi", "DL", 18000000),
        (2, "Mumbai", "MH", 20000000),
        (3, "Chennai", "TN", 12000000),
        (4, "Agra", "UP", 6000000),
        (5, "Bhopal", "MP", 2500000)
    ]
    cur.executemany("INSERT INTO Station VALUES (?, ?, ?, ?);", stations)
    conn.commit()
    return conn

conn = create_sample_db()

# --- QUESTION BANK ---
question_sets = {
    "Easy": [
        {
            "id": 1,
            "question": "List all employee names in alphabetical order.",
            "answer": "SELECT Name FROM Employee ORDER BY Name ASC;",
            "explanation": "ORDER BY sorts results alphabetically."
        },
        {
            "id": 2,
            "question": "Find the average salary of all employees.",
            "answer": "SELECT AVG(Salary) AS Average_Salary FROM Employee;",
            "explanation": "AVG() gives the mean value of a column."
        },
        {
            "id": 3,
            "question": "Show unique departments from Employee table.",
            "answer": "SELECT DISTINCT Department FROM Employee;",
            "explanation": "DISTINCT filters out duplicate values."
        },
    ],
    "Advanced": [
        {
            "id": 4,
            "question": "Find cities that end with vowels (no duplicates).",
            "answer": "SELECT DISTINCT City FROM Station WHERE City LIKE '%a' OR City LIKE '%e' OR City LIKE '%i' OR City LIKE '%o' OR City LIKE '%u';",
            "explanation": "LIKE with '%' matches patterns, DISTINCT removes repeats."
        },
        {
            "id": 5,
            "question": "Find total earnings (Salary * Months) per employee.",
            "answer": "SELECT Name, (Salary * Months) AS Total_Earnings FROM Employee;",
            "explanation": "Arithmetic can be used in SELECT to create new columns."
        },
        {
            "id": 6,
            "question": "Find the difference between highest and lowest population.",
            "answer": "SELECT MAX(Population) - MIN(Population) AS Difference FROM Station;",
            "explanation": "MAX and MIN give you range difference."
        },
    ],
    "Mock Test": [
        {
            "id": 7,
            "question": "Find all employees whose salary is greater than the average salary.",
            "answer": "SELECT Name, Salary FROM Employee WHERE Salary > (SELECT AVG(Salary) FROM Employee);",
            "explanation": "Subqueries allow comparing a value to an aggregate."
        },
        {
            "id": 8,
            "question": "Find departments having more than one employee.",
            "answer": "SELECT Department, COUNT(*) FROM Employee GROUP BY Department HAVING COUNT(*) > 1;",
            "explanation": "HAVING is used with GROUP BY for aggregate conditions."
        },
        {
            "id": 9,
            "question": "Find the city with the smallest population.",
            "answer": "SELECT City FROM Station ORDER BY Population ASC LIMIT 1;",
            "explanation": "ORDER BY + LIMIT selects the smallest or largest entry."
        }
    ]
}

# --- SESSION STATE TRACKING ---
if "attempts" not in st.session_state:
    st.session_state.attempts = {}
if "last_question" not in st.session_state:
    st.session_state.last_question = None

# --- DIFFICULTY & QUESTION SELECTION ---
difficulty = st.selectbox("Select Difficulty Level:", list(question_sets.keys()))
questions = question_sets[difficulty]

st.subheader(f"🧩 Choose a {difficulty} Question:")
question_texts = [f"Q{i['id']}. {i['question']}" for i in questions]
selected = st.selectbox("Select a question:", question_texts)
selected_q = next(q for q in questions if selected.startswith(f"Q{q['id']}"))

# Reset attempts on question switch
if st.session_state.last_question != selected_q["id"]:
    st.session_state.attempts[selected_q["id"]] = 0
    st.session_state.last_question = selected_q["id"]

st.write("### 💡 Your Task:")
st.info(selected_q["question"])
user_query = st.text_area("Write your SQL query here:", height=120)

# --- EXECUTE & CHECK ANSWER ---
if st.button("Run Query 🚀"):
    qid = selected_q["id"]
    st.session_state.attempts[qid] += 1
    attempt_count = st.session_state.attempts[qid]

    st.write(f"🧮 Attempt: {attempt_count}/4")

    try:
        df_user = pd.read_sql_query(user_query, conn)
        df_correct = pd.read_sql_query(selected_q["answer"], conn)

        if df_user.equals(df_correct):
            st.success("✅ Correct Answer! Great job!")
            st.dataframe(df_user)
            st.session_state.attempts[qid] = 0  # reset on success

        else:
            st.warning("❌ Not quite right. Try again!")
            st.dataframe(df_user)

            if attempt_count >= 4:
                st.error("💡 You've reached 4 attempts. Here's the correct answer:")
                st.code(selected_q["answer"], language="sql")
                st.write("### 💬 Explanation:")
                st.info(selected_q["explanation"])
                st.write("### 📊 Expected Output:")
                st.dataframe(df_correct)

    except Exception as e:
        st.error(f"⚠️ Error running your query: {e}")

st.markdown("---")
st.caption("Made with ❤️ for SQL learning by Dhrubo Bhattacharjee")
