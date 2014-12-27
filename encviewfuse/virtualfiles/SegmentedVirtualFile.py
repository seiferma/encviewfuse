
import os
from threading import RLock
from encviewfuse.virtualfiles.VirtualFile import VirtualFile
from encviewfuse.SegmentUtils import SegmentUtils

class LazyFile(object):
    def __init__(self, absPath):
        self.path = absPath
        self.file = None
        self.lock = RLock()
        
    def getPath(self):
        return self.path
        
    def read(self, offset, length):
        with self.lock:
            f = self.__getFile()
            f.seek(offset)
            return f.read(length)
    
    def closeFile(self):
        with self.lock:
            if self.file is not None:
                self.file.close()
                
    def __getFile(self):
        with self.lock:
            if self.file is None:
                self.file = open(self.path, "rb")
            return self.file

class SegmentedVirtualFile(VirtualFile):
    
    def __init__(self, absRootPath, segmentSize):
        super(SegmentedVirtualFile, self).__init__(absRootPath)
        self.allSegments = self.__findAllSegments(absRootPath)
        self.segmentSize = segmentSize

    def mtime(self):
        return os.path.getmtime(self.allSegments[0].getPath())
    
    def read(self, offset, size):
        firstSegmentIndex = 0
        segmentOffset = offset
        if self.segmentSize is not None:
            firstSegmentIndex = offset // self.segmentSize
            segmentOffset = offset - (firstSegmentIndex * self.segmentSize)
        
        data = b""
        remainingSize = size
        for segment in self.allSegments[firstSegmentIndex:]:
            readData = segment.read(segmentOffset, remainingSize)
            remainingSize -= len(readData)
            data += readData
            segmentOffset = 0
            if remainingSize <= 0:
                break
        
        return data
    
    def size(self):
        lastSegmentSize = os.path.getsize(self.allSegments[-1].getPath())
        if self.segmentSize is None:
            return lastSegmentSize
        return (len(self.allSegments) - 1) * self.segmentSize + lastSegmentSize
    
    def closeFileHandle(self):
        for segment in self.allSegments:
            segment.closeFile()
            
    def __findAllSegments(self, path):
        absRootPathDir = os.path.dirname(path)
        fileName = os.path.basename(path)
        segmentName, segmentNumber = SegmentUtils.splitSegmentPath(fileName)
        if segmentNumber is None and os.path.exists(path):
            return [LazyFile(path)]
        
        entries = list()
        for entry in os.listdir(absRootPathDir):
            entryBase, _ = SegmentUtils.splitSegmentPath(entry)
            if entryBase == segmentName:
                entries.append(LazyFile(os.path.join(absRootPathDir, entry)))
        entries.sort(key=lambda x: SegmentUtils.splitSegmentPath(x.getPath())[1])
        return entries
