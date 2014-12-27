from encviewfuse.encryption.Encryption import MalformedInputException
from encviewfuse.filehandlecontainers.SegmentedFileHandleContainer import SegmentedVirtualFileHandleContainer
from encviewfuse.implementations import Commons
from encviewfuse.implementations.Commons import EncryptedViewFuseBase
from encviewfuse.virtualfiles.SegmentedVirtualFile import SegmentedVirtualFile
from encviewfuse.SegmentUtils import SegmentUtils
from fuse import FUSE, FuseOSError
from errno import ENOENT
import os, stat


class PathEncryptor(object):
    def __init__(self, root, encryption):
        self.root = root
        self.encryption = encryption
        
    def encryptToAbsolutePath(self, path):
        return self.root + self.encryption.encryptPath(path)
    

class DecViewFuse(EncryptedViewFuseBase):
    
    def __init__(self, root, secret, maxFileSize):
        super(DecViewFuse, self).__init__(root, secret, maxFileSize, SegmentedVirtualFileHandleContainer())
        self.pathEncryptor = PathEncryptor(self.root, self.encryption)
        self.fileHandleContainer.setPathEncryptor(self.pathEncryptor)
        self.fileHandleContainer.setMaxFileSize(self.maxFileSize)

    def read(self, path, size, offset, fh):
        virtualFile = self.fileHandleContainer.getHandle(fh)
        return self.encryption.decryptedContent(virtualFile, offset, size)

    def getattr(self, path, fh=None):
        try:

            absRootPath = self.__encryptToAbsolutePath(path)
            if not os.path.exists(absRootPath):
                absRootPath = SegmentUtils.joinSegmentPath(absRootPath, 0)
            
            st = os.lstat(absRootPath)
            stats = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
            stats['st_mode'] = st.st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            
            if os.path.isfile(absRootPath):
                virtualSegmentedFile = SegmentedVirtualFile(absRootPath, self.maxFileSize)
                stats['st_size'] = self.encryption.decryptedFileSize(virtualSegmentedFile)
                
            return stats
        except MalformedInputException:
            raise FuseOSError(ENOENT)

    def _EncryptedViewFuseBase__convertViewPathToAbsoluteRootPath(self, path):
        return self.__encryptToAbsolutePath(path)

    def _EncryptedViewFuseBase__processReadDirEntry(self, absRootPath, entry):
        dirContent = list()
        segmentFreeEntry, segmentNumber = SegmentUtils.splitSegmentPath(entry)
        if segmentNumber is None or segmentNumber is 0:
            dirContent.append(self.encryption.decryptFileName(segmentFreeEntry))
        return dirContent

    def _EncryptedViewFuseBase__isViewPathAccessible(self, path, mode):
        absRootPath = self.__encryptToAbsolutePath(path)
        if not os.path.exists(absRootPath):
            absRootPath = absRootPath + '.0'
        return os.access(absRootPath, mode)
        
    def __encryptToAbsolutePath(self, path):
        return self.pathEncryptor.encryptToAbsolutePath(path)



def main():
    args = Commons.parseArguments()
    fuse = FUSE(DecViewFuse(args.rootdir, args.secretKey, args.maxFileSize), args.mountpoint)

if __name__ == '__main__':
    main()
