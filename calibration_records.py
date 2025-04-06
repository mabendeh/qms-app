class CalibrationRecord:
    def __init__(self, equipment_id, equipment_name, calibration_date, calibration_result, calibrated_by, next_calibration_date):
        self.record_id = str(uuid.uuid4())[:8]
        self.equipment_id = equipment_id
        self.equipment_name = equipment_name
        self.calibration_date = calibration_date
        self.calibration_result = calibration_result
        self.calibrated_by = calibrated_by
        self.next_calibration_date = next_calibration_date
        self.recorded_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
