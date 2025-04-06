import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime

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

# Main application
if not st.session_state.logged_in:
    login()
else:
    st.set_page_config(page_title="QMS Cloud", layout="wide")
    st.title("🛠️ QMS Web System (IATF & ASI Ready)")

    menu = ["Upload Document", "View Documents"]
    choice = st.sidebar.radio("📂 Navigation", menu)

    if choice == "Upload Document" and st.session_state.role == "admin":
        upload_document()
    elif choice == "View Documents":
        document_table()
import uuid
from datetime import datetime

class Document:
    def __init__(self, title, doc_type, revision, effective_date, department, owner, status, file_path, uploaded_by):
        self.doc_id = str(uuid.uuid4())[:8]
        self.title = title
        self.type = doc_type
        self.revision = revision
        self.effective_date = effective_date
        self.department = department
        self.owner = owner
        self.status = status
        self.file_path = file_path
        self.uploaded_by = uploaded_by
        self.upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.approval_status = "Pending"

class NonConformanceReport:
    def __init__(self, date, shift, line, part_number, defect_type, description, qty_affected, immediate_action, disposition, status, owner, closure_date):
        self.nc_id = str(uuid.uuid4())[:8]
        self.date = date
        self.shift = shift
        self.line = line
        self.part_number = part_number
        self.defect_type = defect_type
        self.description = description
        self.qty_affected = qty_affected
        self.immediate_action = immediate_action
        self.disposition = disposition
        self.status = status
        self.owner = owner
        self.closure_date = closure_date

class RiskEntry:
    def __init__(self, date, risk_description, mitigation_plan, status, owner, closure_date):
        self.risk_id = str(uuid.uuid4())[:8]
        self.date = date
        self.risk_description = risk_description
        self.mitigation_plan = mitigation_plan
        self.status = status
        self.owner = owner
        self.closure_date = closure_date

class TrainingRecord:
    def __init__(self, date, employee_name, training_title, training_description, trainer, status):
        self.training_id = str(uuid.uuid4())[:8]
        self.date = date
        self.employee_name = employee_name
        self.training_title = training_title
        self.training_description = training_description
        self.trainer = trainer
        self.status = status

class SupplierQualityEntry:
    def __init__(self, date, supplier_name, issue_description, corrective_action, status, owner, closure_date):
        self.supplier_id = str(uuid.uuid4())[:8]
        self.date = date
        self.supplier_name = supplier_name
        self.issue_description = issue_description
        self.corrective_action = corrective_action
        self.status = status
        self.owner = owner
        self.closure_date = closure_date
        import streamlit as st
import pandas as pd
import os
from datetime import datetime
from models import Document, NonConformanceReport, RiskEntry, TrainingRecord, SupplierQualityEntry

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

# Main application
if not st.session_state.logged_in:
    login()
else:
    st.set_page_config(page_title="QMS Cloud", layout="wide")
    st.title("🛠️ QMS Web System (IATF & ASI Ready)")

    menu = ["Upload Document", "View Documents"]
    choice = st.sidebar.radio("📂 Navigation", menu)

    if choice == "Upload Document" and st.session_state.role == "admin":
        upload_document()
    elif choice == "View Documents":
        document_table()
