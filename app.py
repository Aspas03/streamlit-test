import streamlit as st
import sqlite3

st.title("🧪 Streamlit Test App")

# Connect to a test database
conn = sqlite3.connect("test.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT)")
conn.commit()

# Simple user interaction
user_input = st.text_input("Enter a test note:")
if st.button("Save Note"):
    c.execute("INSERT INTO notes (text) VALUES (?)", (user_input,))
    conn.commit()
    st.success("Note saved to SQLite!")

# Display stored data
st.subheader("Saved Notes:")
c.execute("SELECT * FROM notes")
rows = c.fetchall()
for row in rows:
    st.write(f"- {row[1]}")

conn.close()