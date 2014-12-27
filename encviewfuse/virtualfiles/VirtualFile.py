from abc import ABCMeta, abstractmethod
import os

class VirtualFile(object, metaclass=ABCMeta):
    
    def __init__(self, name):
        self.name = name
        self.encryptionDictionary = dict()
    
    def name(self):
        return self.name
    
    def basename(self):
        return os.path.basename(self.name)
      
    def encryptionDict(self):
        return self.encryptionDictionary
    
    @abstractmethod
    def mtime(self):
        '''
        Returns the modification time of the file
        '''
    
    @abstractmethod
    def read(self, offset, size):
        '''
        Returns the read bytes from offset with the given size
        or less if EOF is reached.
        '''
    
    @abstractmethod
    def size(self):
        '''
        Returns the size of the file
        '''
