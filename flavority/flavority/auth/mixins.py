
class UserMixin:

    def __init__(self, id = None):
        self.__id_stub = id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True
        
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return self.__id_stub

class AnonymousMixin(UserMixin):
    
    def is_authenticated(self):
        return False
        
    def is_anonymous(self):
        return True

