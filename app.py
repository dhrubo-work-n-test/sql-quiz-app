import streamlit as st
import sqlite3
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="SQL Practice Game 🎯", page_icon="💾", layout="centered")

st.title("🎯 SQL Practice Game")
st.write("Test your SQL skills like HackerRank! Type your query and check instantly if it's correct 🚀")

# --- STAGE 1: SAMPLE DATABASE CREATION ---
@st.cache_resource
def create_sample_db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    # Create Employee table
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

    # Create Station table
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

# --- STAGE 2: QUESTIONS ---
questions = [
    {
        "id": 1,
        "question": "List all employee names in alphabetical order.",
        "answer": "SELECT Name FROM Employee ORDER BY Name ASC;",
        "explanation": "We use ORDER BY to sort names alphabetically."
    },
    {
        "id": 2,
        "question": "Find the average salary of all employees.",
        "answer": "SELECT AVG(Salary) AS Average_Salary FROM Employee;",
        "explanation": "AVG() returns the average of numeric values."
    },
    {
        "id": 3,
        "question": "Display all cities that end with vowels (no duplicates).",
        "answer": "SELECT DISTINCT City FROM Station WHERE City LIKE '%a' OR City LIKE '%e' OR City LIKE '%i' OR City LIKE '%o' OR City LIKE '%u';",
        "explanation": "We use LIKE with wildcards and DISTINCT to avoid repetition."
    },
    {
        "id": 4,
        "question": "Find the total earnings (Salary * Months) for each employee.",
        "answer": "SELECT Name, (Salary * Months) AS Total_Earnings FROM Employee;",
        "explanation": "Arithmetic operators can be used directly inside SELECT."
    },
    {
        "id": 5,
        "question": "Find the difference between the highest and lowest population.",
        "answer": "SELECT MAX(Population) - MIN(Population) AS Difference FROM Station;",
        "explanation": "MAX and MIN are aggregation functions that find extreme values."
    }
]

# --- TRACK USER ATTEMPTS ---
if "attempts" not in st.session_state:
    st.session_state.attempts = {}
if "last_question" not in st.session_state:
    st.session_state.last_question = None

# --- QUESTION SELECT ---
st.subheader("🧩 Choose a Question:")
question_texts = [f"Q{i['id']}. {i['question']}" for i in questions]
selected = st.selectbox("Select a question:", question_texts)

selected_q = next(q for q in questions if selected.startswith(f"Q{q['id']}"))

# Reset attempts if question changes
if st.session_state.last_question != selected_q["id"]:
    st.session_state.attempts[selected_q["id"]] = 0
    st.session_state.last_question = selected_q["id"]


st.write("### 💡 Your Task:")
st.info(selected_q["question"])

user_query = st.text_area("Write your SQL query here:", height=120)

if st.button("Run Query 🚀"):
    qid = selected_q["id"]
    st.session_state.attempts[qid] += 1
    attempt_count = st.session_state.attempts[qid]

    st.write(f"🧮 Attempt: {attempt_count}/4")

    try:
        df_user = pd.read_sql_query(user_query, conn)
        df_correct = pd.read_sql_query(selected_q["answer"], conn)

        if df_user.equals(df_correct):
            st.success("✅ Correct Answer! Well done!")
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
                st.dataframe(df_correct)

    except Exception as e:
        st.error(f"⚠️ Error running your query: {e}")

st.markdown("---")
st.caption("Made with ❤️ for SQL learning by Dhrubo Bhattacharjee")
