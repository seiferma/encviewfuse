from threading import Lock
from deterministic_encryption_utils.encryption.VirtualFile import VirtualFile

class FileHandleContainer(object):
    
    def __init__(self):
        self.handles = dict()
        self.freeIndices = list()
        self.lock = Lock()
    
    def registerHandle(self, path, flags):
        with self.lock:
            fileHandleObject = VirtualFile(path, flags)
            fileHandleIndex = self.__getNextFreeIndex()
            self.handles[fileHandleIndex] = fileHandleObject
            return fileHandleIndex
    
    def getHandle(self, index):
        with self.lock:
            if index not in self.handles.keys():
                raise ValueError('The given index "{0}" is not valid.'.format(index))
            return self.handles[index]
    
    def unregisterHandle(self, index):
        if index is 0:
            return
        with self.lock:
            if index not in self.handles.keys():
                raise ValueError('The given index "{0}" is not valid.'.format(index))
            self.freeIndices.append(index)
            handleObject = self.handles.pop(index)
            handleObject.closeFileHandle()
        
    def __getNextFreeIndex(self):
        if len(self.freeIndices) > 0:
            return self.freeIndices.pop()
        return len(self.handles) + 1 # 0 is a special handle
