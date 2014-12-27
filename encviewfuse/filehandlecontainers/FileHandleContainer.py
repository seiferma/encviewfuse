from abc import ABCMeta, abstractmethod
from threading import Lock

class FileHandleContainer(object, metaclass=ABCMeta):
    def __init__(self):
        self.handles = dict()
        self.freeIndices = list()
        self.lock = Lock()
    
    def registerHandle(self, path):
        with self.lock:
            fileHandleObject = self.__createHandleObject(path)
            fileHandleIndex = self.__getNextFreeIndex()
            self.handles[fileHandleIndex] = fileHandleObject
            return fileHandleIndex
    
    def getHandle(self, index):
        with self.lock:
            return self.handles[index]
    
    def unregisterHandle(self, index):
        with self.lock:
            if index not in self.handles.keys():
                return None
            self.freeIndices.append(index)
            handleObject = self.handles.pop(index)
            self.__cleanupHandleObject(handleObject)
        
    def __getNextFreeIndex(self):
        if len(self.freeIndices) > 0:
            return self.freeIndices.pop()
        return len(self.handles)
        
    @abstractmethod
    def __createHandleObject(self, path):
        '''
        Creates the file handle object for the given path.
        '''
        
    @abstractmethod
    def __cleanupHandleObject(self, handleObject):
        '''
        Cleans up the given handle object.
        '''
