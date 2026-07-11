"""Cross-module domain errors shared by public business-app interfaces."""


class DomainValidationError(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__("Domain payload failed validation.")


class DomainInvalidStateError(Exception):
    pass


class DomainPermissionDenied(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class DomainObjectAccessDenied(Exception):
    def __init__(self, object_access):
        self.object_access = object_access
        super().__init__("Object access denied.")


class DomainNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
