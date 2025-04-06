import streamlit as st
import pandas as pd
import os
from datetime import datetime
from models import Document, NonConformanceReport, RiskEntry, TrainingRecord, SupplierQualityEntry, CAPA, CustomerComplaint
import capa
import customer_complaints

# Initialize session state variables
def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

initialize_session_state()

# User credentials (plain text for simplicity)
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "john": {"password": "approver123", "role": "approver"},
    "maria": {"password": "viewer123", "role": "viewer"}
}

# Utility functions
def load_database(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_database(df, file):
    try:
        df.to_csv(file, index=False)
    except IOError as e:
        st.error(f"Error saving database: {e}")

# Login function
def login():
    st.title("🔐 QMS Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = users.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.success(f"Welcome, {username}! Role: {st.session_state.role}")
        else:
            st.error("Invalid username or password")

# Document Control Module
DOC_DB = "document_db.csv"
os.makedirs("uploaded_documents", exist_ok=True)

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
                filename = f"{str(uuid.uuid4())[:8]}_{file.name}"
                file_path = os.path.join("uploaded_documents", filename)
                with open(file_path, "wb") as f:
                    f.write(file.read())
                doc = Document(title, doc_type, revision, effective_date, department, owner, status, file_path, uploaded_by)
                new_doc = doc.__dict__
                db = load_database(DOC_DB, [])
                db = db.append(new_doc, ignore_index=True)
                save_database(db, DOC_DB)
                st.success("✅ Document uploaded successfully!")
            except IOError as e:
                st.error(f"Error uploading document: {e}")

def document_table():
    st.header("📁 Document Library")
    db = load_database(DOC_DB, [])
    if db.empty:
        st.info("No documents uploaded yet.")
        return
    filter_type = st.selectbox("Filter by Type", ["All"] + db["type"].unique().tolist())
    if filter_type != "All":
        db = db[db["type"] == filter_type]
    st.dataframe(db)

# Dashboard function
def dashboard():
    st.set_page_config(page_title="QMS Cloud", layout="wide")
    st.title("🛠️ QMS Web System (IATF & ASI Ready)")

    menu = [
        "Upload Document", "View Documents", "New NC Report", "View NC Reports",
        "New Risk Entry", "View Risk Reports", "New Training Record", "View Training Records",
        "New Supplier Quality Entry", "View Supplier Quality Reports", "New CAPA Entry", "View CAPA Reports",
        "New Customer Complaint", "View Customer Complaints"
    ]
    choice = st.sidebar.radio("📂 Navigation", menu)

    if choice == "Upload Document" and st.session_state.role == "admin":
        upload_document()
    elif choice == "View Documents":
        document_table()
    elif choice == "New NC Report":
        non_conformance_entry()
    elif choice == "View NC Reports":
        nc_report_view()
    elif choice == "New Risk Entry":
        risk_entry()
    elif choice == "View Risk Reports":
        risk_report_view()
    elif choice == "New Training Record":
        training_entry()
    elif choice == "View Training Records":
        training_report_view()
    elif choice == "New Supplier Quality Entry":
        supplier_entry()
    elif choice == "View Supplier Quality Reports":
        supplier_report_view()
    elif choice == "New CAPA Entry":
        capa.capa_entry()
    elif choice == "View CAPA Reports":
        capa.capa_report_view()
    elif choice == "New Customer Complaint":
        customer_complaints.complaint_entry()
    elif choice == "View Customer Complaints":
        customer_complaints.complaint_report_view()

# Main application
if not st.session_state.logged_in:
    login()
else:
    dashboard()
