from ftplib import FTP
from pathlib import PurePath, Path
from zipfile import ZipFile
import os


class FTPClientModel:
    isConnected = False
    server = None
    username = 'dex'
    password = '123'
    address = '127.0.0.1'
    port = 8009

    def __init__(self):
        self.server = FTP()

    def connect(self, username=None, password=None, address=None, port=None):
        self.server.connect(address or self.address, port or self.port)
        self.server.login(username or self.username, password or self.password)
        self.isConnected = True
        return self

    def disconnect(self):
        if self.isConnected:
            self.isConnected = False
            self.server.quit()

    def list_dir(self, *args):
        list_res = []
        list_fname = []
        dirs = args[0]
        # Using mlsd not retrlines. Kalau mau buat callback di retrlines, terserah.
        dir_yield = self.server.mlsd(dirs, facts=['types', 'size', 'perm'])
        for path in dir_yield:
            abs_path = os.path.abspath(path[0])
            file_path = PurePath(abs_path).as_uri()
            list_fname.append(path[0])
            list_res.append(file_path)
        return {'filenames': list_fname, 'paths': list_res}

    def download(self, *args):
        res = []

        for arg in args:
            fname = f"{arg}"
            if Path(arg).is_dir():
                with ZipFile(arg) as z:
                    fname = f"{arg}.zip"
                    z.write(filename=fname)

            with open(fname, 'wb') as fd:
                self.server.retrbinary('RETR ' + fname, fd.write, 1024)
                res.append(fd)
                print(fd)

        return res

    def upload(self, *args):
        res = []

        for arg in args:
            with open(arg, 'rb') as fd:
                self.server.storbinary('STOR ', arg, fd, 1024)

    def change_dir(self, **kwargs):
        global to_path
        if kwargs is not None:
            for key, val in kwargs.items():
                if key == 'from':
                    from_path = val
                elif key == 'to':
                    to_path = val

            self.server.cwd(to_path)


if __name__ == '__main__':
    client = FTPClientModel()
    client.connect()
    result = client.list_dir('.')
    print(result)
