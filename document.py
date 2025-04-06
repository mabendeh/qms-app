import uuid
from datetime import datetime

class Document:
    def __init__(self, title, doc_type, revision, effective_date, department,
                 owner, status, file_path, uploaded_by):
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
        self.uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
