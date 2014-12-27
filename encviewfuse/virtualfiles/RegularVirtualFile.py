from encviewfuse.virtualfiles.VirtualFile import VirtualFile
import os

class RegularVirtualFile(VirtualFile):
    
    def __init__(self, absRootPath):
        super(RegularVirtualFile, self).__init__(absRootPath)
        self.absRootPath = absRootPath
        
    def mtime(self):
        return os.path.getmtime(self.absRootPath)
    
    def read(self, offset, size):
        with open(self.absRootPath, "rb") as f:
            f.seek(offset)
            return f.read(size)
    
    def size(self):
        return os.path.getsize(self.absRootPath)
