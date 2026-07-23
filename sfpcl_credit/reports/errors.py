class ReportPermissionDenied(Exception):
    """The actor lacks report permission or the required persisted read scope."""


class ReportValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__("Report query failed validation.")
