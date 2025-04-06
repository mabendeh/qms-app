import subprocess
import sys

def install_dependencies():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv", "bcrypt"])

try:
    from dotenv import load_dotenv
    import bcrypt
except ImportError:
    install_dependencies()
    from dotenv import load_dotenv
    import bcrypt

import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import matplotlib.pyplot as plt
import hashlib

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

load_dotenv()

# User credentials (hashed passwords)
users = {
    "admin": {"password": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()), "role": "admin"},
    "john": {"password": bcrypt.hashpw("approver123".encode(), bcrypt.gensalt()), "role": "approver"},
    "maria": {"password": bcrypt.hashpw("viewer123".encode(), bcrypt.gensalt()), "role": "viewer"}
}

# Login function
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

# Load database function
def load_database(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

# Save database function
def save_database(df, file):
    try:
        df.to_csv(file, index=False)
    except IOError as e:
        st.error(f"Error saving database: {e}")

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

# Non-Conformance Module
NC_DB = "nonconformance_db.csv"

def non_conformance_entry():
    st.header("⚠️ New Non-Conformance Report")
    with st.form("nc_form"):
        date = st.date_input("Date")
        shift = st.selectbox("Shift", ["A", "B", "C"])
        line = st.text_input("Line/Station")
        part_number = st.text_input("Part Number")
        defect_type = st.text_input("Defect Type")
        description = st.text_area("Description")
        qty_affected = st.number_input("Quantity Affected", min_value=1)
        immediate_action = st.text_input("Immediate Action Taken")
        disposition = st.selectbox("Disposition", ["Scrap", "Rework", "Use As-Is", "Hold"])
        status = st.selectbox("Status", ["Open", "Under Review", "Closed"])
        owner = st.text_input("Owner")
        closure_date = st.date_input("Closure Date", value=datetime.today())
        submitted = st.form_submit_button("Submit NC Report")

        if submitted:
            try:
                nc_id = str(uuid.uuid4())[:8]
                new_nc = {
                    "nc_id": nc_id, "date": date, "shift": shift, "line": line,
                    "part_number": part_number, "defect_type": defect_type,
                    "description": description, "qty_affected": qty_affected,
                    "immediate_action": immediate_action, "disposition": disposition,
                    "status": status, "owner": owner, "closure_date": closure_date
                }
                columns = list(new_nc.keys())
                db = load_database(NC_DB, columns)
                db = db.append(new_nc, ignore_index=True)
                save_database(db, NC_DB)
                st.success("✅ Non-Conformance Report Submitted!")
            except IOError as e:
                st.error(f"Error submitting report: {e}")

def nc_report_view():
    st.header("📋 Non-Conformance Reports")
    columns = ["nc_id", "date", "shift", "line", "part_number", "defect_type",
               "description", "qty_affected", "immediate_action", "disposition",
               "status", "owner", "closure_date"]
    db = load_database(NC_DB, columns)
    if db.empty:
        st.info("No non-conformance reports submitted yet.")
        return
    st.dataframe(db)

# Risk Management Module
RISK_DB = "risk_db.csv"

def risk_entry():
    st.header("⚠️ New Risk Entry")
    with st.form("risk_form"):
        date = st.date_input("Date")
        risk_description = st.text_area("Risk Description")
        mitigation_plan = st.text_area("Mitigation Plan")
        status = st.selectbox("Status", ["Identified", "Mitigated", "Closed"])
        owner = st.text_input("Owner")
        closure_date = st.date_input("Closure Date", value=datetime.today())
        submitted = st.form_submit_button("Submit Risk Entry")

        if submitted:
            try:
                risk_id = str(uuid.uuid4())[:8]
                new_risk = {
                    "risk_id": risk_id, "date": date, "risk_description": risk_description,
                    "mitigation_plan": mitigation_plan, "status": status, "owner": owner,
                    "closure_date": closure_date
                }
                columns = list(new_risk.keys())
                db = load_database(RISK_DB, columns)
                db = db.append(new_risk, ignore_index=True)
                save_database(db, RISK_DB)
                st.success("✅ Risk Entry Submitted!")
            except IOError as e:
                st.error(f"Error submitting risk entry: {e}")

def risk_report_view():
    st.header("📋 Risk Reports")
    columns = ["risk_id", "date", "risk_description", "mitigation_plan", "status", "owner", "closure_date"]
    db = load_database(RISK_DB, columns)
    if db.empty:
        st.info("No risk entries submitted yet.")
        return
    st.dataframe(db)

# Training Records Module
TRAINING_DB = "training_db.csv"

def training_entry():
    st.header("📚 New Training Record")
    with st.form("training_form"):
        date = st.date_input("Date")
        employee_name = st.text_input("Employee Name")
        training_title = st.text_input("Training Title")
        training_description = st.text_area("Training Description")
        trainer = st.text_input("Trainer")
        status = st.selectbox("Status", ["Completed", "Pending"])
        submitted = st.form_submit_button("Submit Training Record")

        if submitted:
            try:
                training_id = str(uuid.uuid4())[:8]
                new_training = {
                    "training_id": training_id, "date": date, "employee_name": employee_name,
                    "training_title": training_title, "training_description": training_description,
                    "trainer": trainer, "status": status
                }
                columns = list(new_training.keys())
                db = load_database(TRAINING_DB, columns)
                db = db.append(new_training, ignore_index=True)
                save_database(db, TRAINING_DB)
                st.success("✅ Training Record Submitted!")
            except IOError as e:
                st.error(f"Error submitting training record: {e}")

def training_report_view():
    st.header("📋 Training Records")
    columns = ["training_id", "date", "employee_name", "training_title", "training_description", "trainer", "status"]
    db = load_database(TRAINING_DB, columns)
    if db.empty:
        st.info("No training records submitted yet.")
        return
    st.dataframe(db)

# Supplier Quality Module
SUPPLIER_DB = "supplier_db.csv"

def supplier_entry():
    st.header("🏭 New Supplier Quality Entry")
    with st.form("supplier_form"):
        date = st.date_input("Date")
        supplier_name = st.text_input("Supplier Name")
        issue_description = st.text_area("Issue Description")
        corrective_action = st.text_area("Corrective Action")
        status = st.selectbox("Status", ["Open", "Resolved", "Closed"])
        owner = st.text_input("Owner")
        closure_date = st.date_input("Closure Date", value=datetime.today())
        submitted = st.form_submit_button("Submit Supplier Quality Entry")

        if submitted:
            try:
                supplier_id = str(uuid.uuid4())[:8]
                new_supplier = {
                    "supplier_id": supplier_id, "date": date, "supplier_name": supplier_name,
                    "issue_description": issue_description, "corrective_action": corrective_action,
                    "status": status, "owner": owner, "closure_date": closure_date
                }
                columns = list(new_supplier.keys())
                db = load_database(SUPPLIER_DB, columns)
                db = db.append(new_supplier, ignore_index=True)
                save_database(db, SUPPLIER_DB)
                st.success("✅ Supplier Quality Entry Submitted!")
            except IOError as e:
                st.error(f"Error submitting supplier quality entry: {e}")

def supplier_report_view():
    st.header("📋 Supplier Quality Reports")
    ▋
