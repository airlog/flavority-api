
class BaseMixin:

    def is_authenticated(self):
        raise NotImplementedError()

    def is_active(self):
        raise NotImplementedError()

    def is_anonymous(self):
        raise NotImplementedError()

    def get_id(self):
        raise NotImplementedError()

class UserMixin(BaseMixin):

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

class AnonymousMixin(BaseMixin):
    
    def is_authenticated(self):
        return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return None
