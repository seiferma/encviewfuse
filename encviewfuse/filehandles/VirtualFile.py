import os
from threading import Lock

class VirtualFile(object):
    
    def __init__(self, absRootPath, flags=os.O_RDONLY):
        if not os.path.isfile(absRootPath):
            raise ValueError('The given path "{0}" has to point to an existing file.'.format(absRootPath))
        self.absRootPath = absRootPath
        self.fd = os.open(absRootPath, flags)
        self.lock = Lock()
        self.encryptionDictionary = dict()
    
    def name(self):
        return self.absRootPath
    
    def basename(self):
        return os.path.basename(self.absRootPath)
        
    def mtime(self):
        return os.path.getmtime(self.absRootPath)
    
    def read(self, offset, size):
        with self.lock:
            os.lseek(self.fd, offset, os.SEEK_SET)
            return os.read(self.fd, size)
    
    def size(self):
        return os.path.getsize(self.absRootPath)

    def closeFileHandle(self):
        os.close(self.fd)
        
    def encryptionDict(self):
        return self.encryptionDictionary
