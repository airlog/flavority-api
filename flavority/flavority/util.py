
class Flavority:

    @staticmethod
    def success(**kwargs):
        d = {key: value for key, value in kwargs.items()}
        d['api_result'] = 'success'
        return d

    @staticmethod
    def failure(message=None, code=None):
        return {
            "api_result": "failure",
            "message": message,
            "code": code,
        }
