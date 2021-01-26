import uuid
class Group:
    def __init__(self, username, name):
        self.name = name
        self.rand_nonce = uuid.uuid4().bytes
        self.rand_nonce = str(int.from_bytes(self.rand_nonce, 'little'))
        # self.random_nonce = random_nonce
        self.participants = [username]
    
    def no_of_participants(self):
        return len(self.participants)

    def add_participants(self):
        pass
