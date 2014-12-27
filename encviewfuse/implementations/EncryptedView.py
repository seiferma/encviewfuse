from encviewfuse.encryption.Encryption import MalformedInputException
from encviewfuse.filehandlecontainers.SingleSegmentFileHandleContainer import SingleSegmentVirtualFileHandleContainer
from encviewfuse.implementations import Commons
from encviewfuse.implementations.Commons import EncryptedViewFuseBase
from encviewfuse.SegmentUtils import SegmentUtils
from fuse import FUSE, FuseOSError
from errno import ENOENT
from math import ceil
import os, stat


class PathDecryptor(object):
    def __init__(self, root, encryption):
        self.root = root
        self.encryption = encryption
        
    def decryptToAbsolutePath(self, path):
        return self.root + self.encryption.decryptPath(path)


class EncViewFuse(EncryptedViewFuseBase):
    
    def __init__(self, root, secret, maxFileSize):
        super(EncViewFuse, self).__init__(root, secret, maxFileSize, SingleSegmentVirtualFileHandleContainer())
        self.pathDecryptor = PathDecryptor(self.root, self.encryption)
        self.fileHandleContainer.setPathDecryptor(self.pathDecryptor)

    def read(self, path, size, offset, fh):
        virtualFile = self.fileHandleContainer.getHandle(fh)
        
        if virtualFile.getSegmentNumber() is None:
            return self.encryption.encryptedContent(virtualFile, offset, size)
        else:
            realOffset = virtualFile.getSegmentNumber() * self.maxFileSize + offset
            realSize = min(size, self.maxFileSize - offset)
            return self.encryption.encryptedContent(virtualFile, realOffset, realSize)
    
    def getattr(self, path, fh=None):
        try:
            segmentFreePath, segmentNumber = SegmentUtils.splitSegmentPath(path)
            absRootPath = self.__decryptToAbsolutePath(segmentFreePath)
            
            if self.maxFileSize is not None and segmentNumber is None and os.path.isfile(absRootPath) and self.__encryptedFileSize(os.path.getsize(absRootPath)) > self.maxFileSize:
                raise FuseOSError(ENOENT)
            
            st = os.lstat(absRootPath)
            stats = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
            stats['st_mode'] = st.st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            
            if os.path.isfile(absRootPath):
                stats['st_size'] = self.__encryptedFileSize(os.path.getsize(absRootPath))
                if segmentNumber is not None:
                    if (segmentNumber + 1) * self.maxFileSize <= stats['st_size']:
                        stats['st_size'] = self.maxFileSize
                    else:
                        stats['st_size'] %= self.maxFileSize
                
            return stats
        except MalformedInputException:
            raise FuseOSError(ENOENT)


    def _EncryptedViewFuseBase__convertViewPathToAbsoluteRootPath(self, path):
        return self.__decryptToAbsolutePath(path)

    def _EncryptedViewFuseBase__processReadDirEntry(self, absRootPath, entry):
        dirContent = list()
        
        # encrypt file name
        absRootPathEntry = os.path.join(absRootPath, entry)
        entryViewName = self.encryption.encryptFileName(entry)
        
        # split large files
        if os.path.isfile(absRootPathEntry):
            encryptedFileSize = self.__encryptedFileSize(os.path.getsize(absRootPathEntry))
            if not self.maxFileSize is None and encryptedFileSize > self.maxFileSize:
                numberOfParts = ceil(encryptedFileSize / self.maxFileSize)
                for i in range(0, numberOfParts):
                    dirContent.append(entryViewName + "." + str(i))
                return dirContent
        
        # return not splitted entry
        dirContent.append(entryViewName)
        return dirContent
    
    def _EncryptedViewFuseBase__isViewPathAccessible(self, path, mode):
        segmentFreePath, _ = SegmentUtils.splitSegmentPath(path)
        absRootPath = self.__decryptToAbsolutePath(segmentFreePath)
        return os.access(absRootPath, mode)
    
    
        
        
    def __decryptToAbsolutePath(self, path):
        return self.pathDecryptor.decryptToAbsolutePath(path)
    
    def __encryptedFileSize(self, fileSizeInBytes):
        return self.encryption.encryptedFileSize(fileSizeInBytes)
    



def main():
    args = Commons.parseArguments()
    fuse = FUSE(EncViewFuse(args.device, args.mountOptions['secret'], args.mountOptions['segmentsize']), args.dir, **args.mountOptions['other'])

if __name__ == '__main__':
    main()
