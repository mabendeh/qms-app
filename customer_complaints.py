class CustomerComplaint:
    def __init__(self, date, customer_name, complaint_description, corrective_action, status, owner, closure_date):
        self.complaint_id = str(uuid.uuid4())[:8]
        self.date = date
        self.customer_name = customer_name
        self.complaint_description = complaint_description
        self.corrective_action = corrective_action
        self.status = status
        self.owner = owner
        self.closure_date = closure_date
