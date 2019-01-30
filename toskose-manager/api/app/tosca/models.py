

class ToskoseNode:
    def __init__(self, id, host, port, username, password):
        self._id = id
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    @property
    def id(self):
        return self._id

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password    
