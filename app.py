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

# User credentials (hashed passwords)
users = {
    "admin": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin"},
    "john": {"password": hashlib.sha256("approver123".encode()).hexdigest(), "role": "approver"},
    "maria": {"password": hashlib.sha256("viewer123".encode()).hexdigest(), "role": "viewer"}
}

def login():
    st.title("🔐 QMS Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = users.get(username)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user and user["password"] == hashed_password:
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

def nc_dashboard():
    st.header("📊 NC Reporting Dashboard")
    columns = ["nc_id", "date", "shift", "line", "part_number", "defect_type",
               "description", "qty_affected", "immediate_action", "disposition",
               "status", "owner", "closure_date"]
    db = load_database(NC_DB, columns)
    if db.empty:
        st.info("No data available for reporting.")
        return

    db["date"] = pd.to_datetime(db["date"], errors='coerce')

    st.subheader("Top Defect Types")
    defect_counts = db["defect_type"].value_counts().nlargest(10)
    st.bar_chart(defect_counts)

    st.subheader("NC Reports Over Time")
    trend = db.groupby(db["date"].dt.to_period("M")).size()
    st.line_chart(trend)

    st.subheader("Disposition Breakdown")
    st.dataframe(db["disposition"].value_counts())

if not st.session_state.logged_in:
    login()
else:
    st.set_page_config(page_title="QMS Cloud", layout="wide")
    st.title("🛠️ QMS Web System (IATF & ASI Ready)")

    menu = ["Upload Document", "View Documents", "New NC Report", "View NC Reports", "NC Dashboard"]
    choice = st.sidebar.radio("📂 Navigation", menu)

    if choice == "Upload Document" and st.session_state.role == "admin":
        upload_document()
    elif choice == "View Documents":
        document_table()
    elif choice == "New NC Report":
        non_conformance_entry()
    elif choice == "View NC Reports":
        nc_report_view()
    elif choice == "NC Dashboard":
        nc_dashboard()
