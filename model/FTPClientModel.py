from ftplib import FTP
from pathlib import PurePath, Path
from zipfile import ZipFile
import os
from urllib import parse


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

    def list_dir(self, *args) -> list:
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

        # TODO: FILES_PATH tidak absolut dari path aslinya
        # return list_dir, files_path
        return list_dir

    def download(self, sourceName, destPath) -> bool:
        sourcePath = os.path.join(self.remoteCurrentPath, sourceName)

        # Not tested yet
        with open(destPath, 'wb') as file:
            self.client.retrbinary(f'RETR {sourcePath}',
                                   callback=lambda data: file.write(data))
        # Force check
        return Path(destPath).is_file()

    def upload(self, sourcePath, destName):
        destPath = os.path.join(self.remoteCurrentPath, destName)
        # CALLBACK not working yet
        # progres = None

        with open(sourcePath, 'rb') as file:
            self.client.storbinary(f'STOR {destPath}',
                                   fp=file, callback=None)

    def change_dir(self, path=".") -> list:
        self.client.cwd(path)

        self.remoteHist.append(path)
        self.remoteCurrentPath = path

        return self.list_dir(path)

    def curr_dir(self):
        return self.client.pwd()


if __name__ == '__main__':
    client = FTPClientModel()
    client.connect()
    # client.upload(f"{os.path.abspath('../file')}\\abc.txt",
    #               "/folder1/testabc.txt")
    result = client.list_dir('.')
    print(result)
    print(client.curr_dir())
    result = client.change_dir('\\folder1/\\folder1_1')
    print(client.curr_dir())
    print(result)
    client.client.quit()
