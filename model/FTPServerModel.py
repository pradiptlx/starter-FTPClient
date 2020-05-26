import os
from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer


class FTPServerModel:
    username = ""
    password = ""
    server = None
    authorizer = None
    handler = None
    address = ('127.0.0.1', 8009)
    default_path = os.path.abspath('../file')
    permission_attr = 'elradfmwMT'

    def __init__(self, address=('127.0.0.1', 8009), username='dex', password='123'):
        self.address = address
        self.password = password
        self.username = username
        self.authorizer_server()
        self.handler_server()
        self.connect()

    def authorizer_server(self, path=None):
        self.authorizer = DummyAuthorizer()
        if path is not None:
            self.default_path = path
        self.authorizer.add_user(self.username, self.password,
                                 self.default_path, self.permission_attr)

    def handler_server(self):
        self.handler = FTPHandler
        self.handler.authorizer = self.authorizer

    def connect(self, **kwargs):
        if self.username == "" and self.password == "":
            raise ValueError("Input username password server")

        self.server = FTPServer(self.address, self.handler)
        self.server.serve_forever()
        # for arg in kwargs:
        #     self.server.arg = arg.values()


if __name__ == '__main__':
    server = FTPServerModel()
