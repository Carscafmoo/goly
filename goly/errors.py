from flask_api import exceptions

class ResourceAlreadyExistsError(exceptions.APIException):
    status_code = 409
    def __init__(self, resource, value):
        self.detail = "Unable to create " + resource + "; value " + value + " already exists" 

    def to_dict(self):
        return {"detail": self.detail}

class UnauthorizedError(exceptions.APIException):
    status_code = 401
    def __init__(self):
        self.detail = "Invalid credentials" 

    def to_dict(self):
        return {"detail": self.detail}    
