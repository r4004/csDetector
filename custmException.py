import json
class customException(Exception):
    def __init__(self, message, code):
        self.code_Error = code
        self.message = message

    def printError(self):
        if not self.message:
            raise self

    def to_json(self):
        return json.dumps({
            "error": self.message,
            "code": self.code_Error
        })