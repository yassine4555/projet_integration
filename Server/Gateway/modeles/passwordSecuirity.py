import json

class passwordSecurity:
    def __init__(self, password, userId):
        self.password = password
        self.userId = userId

    def to_dict(self):
        return {
            "password": self.password,
            "userId": self.userId
        }

