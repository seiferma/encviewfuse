from encviewfuse.filehandlecontainers.FileHandleContainer import FileHandleContainer
from encviewfuse.SegmentUtils import SegmentUtils
from encviewfuse.virtualfiles.SingleSegmentVirtualFile import SingleSegmentVirtualFile

class SingleSegmentVirtualFileHandleContainer(FileHandleContainer):
    
    def __init__(self):
        super(SingleSegmentVirtualFileHandleContainer, self).__init__()
        self.pathDecryptor = None
        
    def setPathDecryptor(self, pathDecryptor):
        self.pathDecryptor = pathDecryptor
        
    def _FileHandleContainer__createHandleObject(self, path):
        segmentFreePath, segmentNumber = SegmentUtils.splitSegmentPath(path)
        absRootPath = self.pathDecryptor.decryptToAbsolutePath(segmentFreePath)
        return SingleSegmentVirtualFile(absRootPath, segmentNumber)
        
    def _FileHandleContainer__cleanupHandleObject(self, handleObject):
        handleObject.closeFileHandle()
