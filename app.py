import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime

# Import your custom modules/classes
from capa import CAPA
from customer_complaints import CustomerComplaint
from document import Document
from nc_report import NonConformanceReport
from risk import RiskEntry
from training import TrainingRecord
from supplier_quality import SupplierQualityEntry

# Define DB paths
DOC_DB = "document_db.csv"
NC_DB = "nonconformance_db.csv"
RISK_DB = "risk_db.csv"
TRAINING_DB = "training_db.csv"
SUPPLIER_DB = "supplier_db.csv"
CAPA_DB = "capa_db.csv"
COMPLAINT_DB = "complaint_db.csv"

# Create directories
os.makedirs("uploaded_documents", exist_ok=True)

# Session State Initialization
def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

initialize_session_state()

# User credentials
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "john": {"password": "approver123", "role": "approver"},
    "maria": {"password": "viewer123", "role": "viewer"}
}

# Utilities
def load_database(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

def save_database(df, file):
    try:
        df.to_csv(file, index=False)
    except IOError as e:
        st.error(f"Error saving database: {e}")

# Login Page
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

# Main Application Navigation
def main_app():
    st.set_page_config(page_title="QMS Cloud", layout="wide")
    st.title("🛠️ QMS Web System (IATF & ASI Ready)")

    menu = {
        "Upload Document": upload_document,
        "View Documents": document_table,
        "New NC Report": non_conformance_entry,
        "View NC Reports": nc_report_view,
        "New Risk Entry": risk_entry,
        "View Risk Reports": risk_report_view,
        "New Training Record": training_entry,
        "View Training Records": training_report_view,
        "New Supplier Quality Entry": supplier_entry,
        "View Supplier Quality Reports": supplier_report_view,
        "New CAPA Entry": capa_entry,
        "View CAPA Reports": capa_report_view,
        "New Customer Complaint": complaint_entry,
        "View Customer Complaints": complaint_report_view,
    }

    choice = st.sidebar.radio("📂 Navigation", list(menu.keys()))

    if choice == "Upload Document" and st.session_state.role != "admin":
        st.warning("Only admin users can upload documents.")
    else:
        menu[choice]()

# Run app
if not st.session_state.logged_in:
    login()
else:
    main_app()
