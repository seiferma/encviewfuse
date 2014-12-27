from encviewfuse.virtualfiles.RegularVirtualFile import RegularVirtualFile
from threading import Lock

class SingleSegmentVirtualFile(RegularVirtualFile):
    
    def __init__(self, absRootPath, segmentNumber):
        super(SingleSegmentVirtualFile, self).__init__(absRootPath)
        self.segmentNumber = segmentNumber
        self.file = open(self.absRootPath, "rb")
        self.lock = Lock()
    
    def read(self, offset, size):
        with self.lock:
            self.file.seek(offset)
            return self.file.read(size)
    
    def getSegmentNumber(self):
        return self.segmentNumber
    
    def closeFileHandle(self):
        self.file.close()
        