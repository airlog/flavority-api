
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

    ##Class constructor.
    def __init__(self, id = None):
        self.__id_stub = id

    ##Method returns:
    #* 'True' if user is authenticated,
    #* 'False' if user is not authenticated
    def is_authenticated(self):
        return True

    ##Method returns:
    #* 'True' if user is active,
    #* 'False' if user is not active
    def is_active(self):
        return True

    ##Method returns:
    #* 'True' if user is not logged in,
    #* 'False' if user is logged in
    def is_anonymous(self):
        return False

    ##Method returns logged user ID from database
    def get_id(self):
        return self.__id_stub

class AnonymousMixin(BaseMixin):

    ##Method returns:
    #* 'True' if user is authenticated,
    #* 'False' if user is not authenticated
    def is_authenticated(self):
        return False

    ##Method returns:
    #* 'True' if user is active,
    #* 'False' if user is not active
    def is_active(self):
        return True

    ##Method returns:
    #* 'True' if user is not logged in,
    #* 'False' if user is logged in
    def is_anonymous(self):
        return True

    ##Method returns user ID from database.
    def get_id(self):
        return None
