import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import matplotlib.pyplot as plt
import hashlib

try:
    from dotenv import load_dotenv
    import bcrypt
    load_dotenv()
except ImportError as e:
    st.error(f"Missing dependency: {e}. Please run 'pip install python-dotenv bcrypt' to install it.")
    st.stop()

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# User credentials (hashed passwords)
users = {
    "admin": {"password": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()), "role": "admin"},
    "john": {"password": bcrypt.hashpw("approver123".encode(), bcrypt.gensalt()), "role": "approver"},
    "maria": {"password": bcrypt.hashpw("viewer123".encode(), bcrypt.gensalt()), "role": "viewer"}
}

def login():
    st.title("🔐 QMS Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = users.get(username)
        if user and bcrypt.checkpw(password.encode(), user["password"]):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.success(f"Welcome, {username}! Role: {st.session_state.role}")
        else:
            st.error("Invalid username or password")

DOC_DB = "document_db.csv"
NC_DB = "nonconformance_db.csv"
os.makedirs("uploaded_documents", exist_ok=True)

def load_database(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_database(df, file):
    try:
        df.to_csv(file, index=False)
    except IOError as e:
        st.error(f"Error saving database: {e}")

def upload_document():
    st.header("📄 Upload New Document")
    with st.form("upload_form"):
        title = st.text_input("Document Title")
        doc_type = st.selectbox("Document Type", ["SOP", "WI", "Form", "Policy", "Checklist"])
        revision = st.text_input("Revision", "A")
        effective_date = st.date_input("Effective Date")
        department = st.text_input("Department")
        owner = st.text_input("Owner")
        status = st.selectbox("Status", ["Draft", "Active", "Obsolete"])
        uploaded_by = st.session_state.username
        file = st.file_uploader("Upload File", type=["pdf", "docx", "xlsx"])
        submitted = st.form_submit_button("Upload Document")

        if submitted and file:
            try:
                doc_id = str(uuid.uuid4())[:8]
                filename = f"{doc_id}_{file.name}"
                file_path = os.path.join("uploaded_documents", filename)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                new_doc = {
                    "doc_id": doc_id, "title": title, "type": doc_type,
                    "revision": revision, "effective_date": effective_date,
                    "department": department, "owner": owner, "status": status,
                    "file_path": file_path, "uploaded_by": uploaded_by,
                    "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "approval_status": "Pending"
                }
                db = load_database(DOC_DB, [])
                db = db.append(new_doc, ignore_index=True)
                save_database(db, DOC_DB)
                st.success("✅ Document uploaded ▋
