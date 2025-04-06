class CAPA:
    def __init__(self, date, issue_description, root_cause, corrective_action, preventive_action, status, owner, closure_date):
        self.capa_id = str(uuid.uuid4())[:8]
        self.date = date
        self.issue_description = issue_description
        self.root_cause = root_cause
        self.corrective_action = corrective_action
        self.preventive_action = preventive_action
        self.status = status
        self.owner = owner
        self.closure_date = closure_date
