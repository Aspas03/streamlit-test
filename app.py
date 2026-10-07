import pandas as pd
import sqlitecloud
import streamlit as st

st.set_page_config(page_title="Streamlit Test App", page_icon="🧪")

st.title("🧪 Streamlit Test App (Live Cloud DB)")

# Fetch connection string from Streamlit Cloud Secrets (or local fallback)
conn_str = st.secrets.get(
    "SQLITECLOUD_CONN_STR", ""
)

if not conn_str:
    st.error(
        "❌ Database Connection String not found! Please configure Secrets in Streamlit Cloud."
    )
    st.stop()

# Connect to SQLite Cloud
try:
    conn = sqlitecloud.connect(conn_str)
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute(
        "CREATE TABLE IF NOT EXISTS test_notes (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)"
    )
    conn.commit()

    # User Input Form
    with st.form("note_form", clear_on_submit=True):
        user_input = st.text_input("Enter a test note:")
        submitted = st.form_submit_button("Save Note")

    if submitted and user_input.strip():
        c.execute(
            "INSERT INTO test_notes (text) VALUES (?)", (user_input.strip(),)
        )
        conn.commit()
        st.success("✅ Note saved permanently to SQLite Cloud!")

    # Display Saved Notes
    st.subheader("📋 Saved Notes in Database")
    df = pd.read_sql_query("SELECT * FROM test_notes", conn)
    st.dataframe(df, use_container_width=True)

    conn.close()

except Exception as e:
    st.error(f"Error connecting to database: {e}")