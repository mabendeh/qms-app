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
                nc = NonConformanceReport(date, shift, line, part_number, defect_type, description, qty_affected, immediate_action, disposition, status, owner, closure_date)
                new_nc = nc.__dict__
                db = load_database(NC_DB, list(new_nc.keys()))
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
                risk = RiskEntry(date, risk_description, mitigation_plan, status, owner, closure_date)
                new_risk = risk.__dict__
                db = load_database(RISK_DB, list(new_risk.keys()))
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
                training = TrainingRecord(date, employee_name, training_title, training_description, trainer, status)
                new_training = training.__dict__
                db = load_database(TRAINING_DB, list(new_training.keys()))
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
                supplier = SupplierQualityEntry(date, supplier_name, issue_description, corrective_action, status, owner, closure_date)
                new_supplier = supplier.__dict__
                db = load_database(SUPPLIER_DB, list(new_supplier.keys()))
                db = db.append(new_supplier, ignore_index=True)
                save_database(db, SUPPLIER_DB)
                st.success("✅ Supplier Quality Entry Submitted!")
            except IOError as e:
                st.error(f"Error submitting supplier quality entry: {e}")

def supplier_report_view():
    st.header("📋 Supplier Quality Reports")
    columns = ["supplier_id", "date", "supplier_name", "issue_description", "corrective_action", "status", "owner", "closure_date"]
    db = load_database(SUPPLIER_DB, columns)
    if db.empty:
        st.info("No supplier quality entries submitted yet.")
        return
    st.dataframe(db)

# CAPA Module
def capa_entry():
    st.header("🛠️ New CAPA Entry")
    with st.form("capa_form"):
        date = st.date_input("Date")
        issue_description = st.text_area("Issue Description")
        root_cause = st.text_area("Root Cause")
        corrective_action = st.text_area("Corrective Action")
        preventive_action = st.text_area("Preventive Action")
        status = st.selectbox("Status", ["Open", "Closed"])
        owner = st.text_input("Owner")
        closure_date = st.date_input("Closure Date", value=datetime.today())
        submitted = st.form_submit_button("Submit CAPA Entry")

        if submitted:
            try:
                capa = CAPA(date, issue_description, root_cause, corrective_action, preventive_action, status, owner, closure_date)
                new_capa = capa.__dict__
                db = load_database(CAPA_DB, list(new_capa.keys()))
                db = db.append(new_capa, ignore_index=True)
                save_database(db, CAPA_DB)
                st.success("✅ CAPA Entry Submitted!")
            except IOError as e:
                st.error(f"Error submitting CAPA entry: {e}")

def capa_report_view():
    st.header("📋 CAPA Reports")
    columns = ["capa_id", "date", "issue_description", "root_cause", "corrective_action", "preventive_action", "status", "owner", "closure_date"]
    db = load_database(CAPA_DB, columns)
    if db.empty:
        st.info("No CAPA entries submitted yet.")
        return
    st.dataframe(db)

# Customer Complaints Module
def complaint_entry():
    st.header("📝 New Customer Complaint")
    with st.form("complaint_form"):
        date = st.date_input("Date")
        customer_name = st.text_input("Customer Name")
        complaint_description = st.text_area("Complaint Description")
        corrective_action = st.text_area("Corrective Action")
        status = st.selectbox("Status", ["Open", "Closed"])
        owner = st.text_input("Owner")
        closure_date = st.date_input("Closure Date", value=datetime.today())
        submitted = st.form_submit_button("Submit Complaint")

        if submitted:
            try:
                complaint = CustomerComplaint(date, customer_name, complaint_description, corrective_action, status, owner, closure_date)
                new_complaint = complaint.__dict__
                db = load_database(COMPLAINT_DB, list(new_complaint.keys()))
                db = db.append(new_complaint, ignore_index=True)
                save_database(db, COMPLAINT_DB)
                st.success("✅ Customer Complaint Submitted!")
            except IOError as e:
                st.error(f"Error submitting complaint: {e}")

def complaint_report_view():
    st.header("📋 Customer Complaints")
    columns = ["complaint_id", "date", "customer_name", "complaint_description", "corrective_action", "status", "owner", "closure_date"]
    db = load_database(COMPLAINT_DB, columns)
    if db.empty:
        st.info("No customer complaints submitted yet.")
        return
    st.dataframe(db)

# Main application
if not st.session_state.logged_in:
    login()
else:
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
