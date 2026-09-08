

class RequestSpecs:
    @staticmethod
    def base_headers():
        return {
            'Content-Type': 'application/json',
            "Accept": "application/json"
        }
        
    @staticmethod
    def auth_headers():
        ...
    