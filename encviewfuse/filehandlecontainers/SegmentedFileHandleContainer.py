from encviewfuse.filehandlecontainers.FileHandleContainer import FileHandleContainer
from encviewfuse.virtualfiles.SegmentedVirtualFile import SegmentedVirtualFile

class SegmentedVirtualFileHandleContainer(FileHandleContainer):
    def __init__(self):
        super(SegmentedVirtualFileHandleContainer, self).__init__()
        self.pathEncryptor = None
        self.maxFileSize = None
        
    def setPathEncryptor(self, pathEncryptor):
        self.pathEncryptor = pathEncryptor
    
    def setMaxFileSize(self, maxFileSize):
        self.maxFileSize = maxFileSize
        
    def _FileHandleContainer__createHandleObject(self, path):
        encryptedPath = self.pathEncryptor.encryptToAbsolutePath(path)
        return SegmentedVirtualFile(encryptedPath, self.maxFileSize)
        
    def _FileHandleContainer__cleanupHandleObject(self, handleObject):
        handleObject.closeFileHandle()
