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
