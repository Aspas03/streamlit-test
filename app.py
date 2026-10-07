import datetime
import pandas as pd
import sqlitecloud
import streamlit as st

st.set_page_config(
    page_title="Streamlit Test Dashboard", page_icon="🧪", layout="wide"
)

st.title("🧪 Streamlit Test Dashboard (SQLite Cloud)")
st.caption(
    "A full-featured demonstration app connected to a persistent SQLite Cloud database."
)

# 1. Fetch Connection String from Streamlit Secrets
conn_str = st.secrets.get("SQLITECLOUD_CONN_STR", "")

if not conn_str:
    st.error(
        "❌ Database Connection String not found! Please configure Secrets in Streamlit Cloud."
    )
    st.stop()


# Helper function to get database connection
def get_db():
    return sqlitecloud.connect(conn_str)


# 2. Initialize Database Tables
try:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS test_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            note TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()
except Exception as e:
    st.error(f"❌ Database Initialization Error: {e}")
    st.stop()

# 3. Sidebar Features: Database Stats & Quick Tools
st.sidebar.header("📊 Database Metrics")
try:
    conn = get_db()
    total_notes = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM test_notes", conn
    ).iloc[0]["count"]
    conn.close()
    st.sidebar.metric(label="Total Saved Notes", value=int(total_notes))
except Exception:
    st.sidebar.metric(label="Total Saved Notes", value="0")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Administration")
if st.sidebar.button("🗑️ Clear All Notes", type="secondary"):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM test_notes")
        conn.commit()
        conn.close()
        st.sidebar.success("Database cleared!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Failed to clear database: {e}")

# 4. Main Application Layout (Tabs)
tab1, tab2 = st.tabs(["📝 Add New Entry", "📋 View & Manage Entries"])

# --- TAB 1: ADD NEW ENTRY ---
with tab1:
    st.subheader("Add Entry to SQLite Cloud")

    with st.form("new_note_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Title:", placeholder="e.g., Streamlit Test")
            category = st.selectbox(
                "Category:", ["Feature Request", "Bug Report", "General Note"]
            )

        with col2:
            status = st.select_slider(
                "Status Priority:", options=["Low", "Medium", "High", "Critical"]
            )
            note_text = st.text_area(
                "Details / Description:",
                placeholder="Write detailed notes here...",
            )

        submitted = st.form_submit_button("🚀 Submit Entry")

        if submitted:
            if not title.strip() or not note_text.strip():
                st.warning("⚠️ Title and Description cannot be empty.")
            else:
                try:
                    conn = get_db()
                    c = conn.cursor()
                    created_at = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    c.execute(
                        """
                        INSERT INTO test_notes (title, category, status, note, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            title.strip(),
                            category,
                            status,
                            note_text.strip(),
                            created_at,
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success("✅ Entry saved permanently to SQLite Cloud!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving entry: {e}")

# --- TAB 2: VIEW & SEARCH ENTRIES ---
with tab2:
    st.subheader("Stored Data Records")

    try:
        conn = get_db()
        df = pd.read_sql_query("SELECT * FROM test_notes ORDER BY id DESC", conn)
        conn.close()

        if df.empty:
            st.info("No records found in the database. Add one in the first tab!")
        else:
            # Search Filter
            search_query = st.text_input("🔍 Search entries by title or note:")
            if search_query.strip():
                df = df[
                    df["title"]
                    .str.contains(search_query, case=False, na=False)
                    | df["note"].str.contains(
                        search_query, case=False, na=False
                    )
                ]

            # Display Data Table
            st.dataframe(df, use_container_width=True)

            # Individual Item Deletion
            st.markdown("---")
            st.subheader("Delete Specific Entry")
            del_col1, del_col2 = st.columns([3, 1])

            with del_col1:
                note_id_to_delete = st.selectbox(
                    "Select ID to Delete:", options=df["id"].tolist()
                )

            with del_col2:
                st.write("")  # Spacing
                st.write("")
                if st.button("🗑️ Delete Selected"):
                    conn = get_db()
                    c = conn.cursor()
                    c.execute(
                        "DELETE FROM test_notes WHERE id = ?",
                        (int(note_id_to_delete),),
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"Entry ID {note_id_to_delete} deleted!")
                    st.rerun()

    except Exception as e:
        st.error(f"Error reading database: {e}")