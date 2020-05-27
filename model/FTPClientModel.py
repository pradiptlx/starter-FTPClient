from ftplib import FTP
from pathlib import PurePath, Path
from zipfile import ZipFile
import os


class FTPClientModel:
    isConnected = False
    client = None
    username = 'dex'
    password = '123'
    address = '127.0.0.1'
    port = 8009

    remoteHist = []
    remoteCurrentPath = f".{os.path.sep}"

    def __init__(self):
        self.client = FTP()

    def connect(self, username=None, password=None, address=None, port=None):
        self.client.connect(address or self.address, port or self.port)
        self.client.login(username or self.username, password or self.password)
        self.isConnected = True
        return self

    def disconnect(self):
        if self.isConnected:
            self.isConnected = False
            self.client.quit()

    def list_dir(self, *args):
        list_dir = []
        files_path = []
        dirs = args[0]
        # Using mlsd not retrlines. Kalau mau buat callback di retrlines, terserah.
        dir_yield = self.client.mlsd(dirs, facts=['type', 'size', 'perm', 'modify', 'create'])
        for path in dir_yield:
            abs_path = os.path.abspath(path[0])
            # file_path = PurePath(abs_path)
            files_path.append(abs_path)

            list_dir.append(path)

        return list_dir, files_path

    def download(self, *args):
        res = []

        for arg in args:
            fname = f"{arg}"
            if Path(arg).is_dir():
                with ZipFile(arg) as z:
                    fname = f"{arg}.zip"
                    z.write(filename=fname)

            with open(fname, 'wb') as fd:
                self.client.retrbinary('RETR ' + fname, fd.write, 1024)
                res.append(fd)
                print(fd)

        return res

    def upload(self, *args):
        res = []

        for arg in args:
            with open(arg, 'rb') as fd:
                self.client.storbinary('STOR ', arg, fd, 1024)

    def change_dir(self, path="."):
        fullpath = os.path.join(self.remoteCurrentPath, os.path.sep + path)
        self.client.cwd(fullpath)

        self.remoteHist.append(fullpath)
        self.remoteCurrentPath = fullpath

        return self.list_dir(fullpath)


if __name__ == '__main__':
    client = FTPClientModel()
    client.connect()
    result = client.list_dir('.')
    print(result)
    result = client.change_dir('folder1')
    print(result)
    client.client.quit()
