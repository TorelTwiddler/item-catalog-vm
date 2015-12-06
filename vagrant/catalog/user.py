import catalog


class User(object):

    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
