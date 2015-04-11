from abc import ABCMeta, abstractmethod
from deterministic_encryption_utils.encryption.Encryption import Encryption
from errno import EPERM, ENOENT
from fuse import FuseOSError, Operations, LoggingMixIn
import os
from encviewfuse.fuse._FileHandleContainer import FileHandleContainer

class FuseFsBase(LoggingMixIn, Operations, metaclass=ABCMeta):
    
    def __init__(self, root, secret, fileSaltProvider, filenameSaltProvider):
        self.root = os.path.realpath(root)
        self.encryption = Encryption(secret, fileSaltProvider, filenameSaltProvider)
        self.fileHandleContainer = FileHandleContainer()

    def __call__(self, op, path, *args):
        return super(FuseFsBase, self).__call__(op, path, *args)

    @abstractmethod
    def __convertViewPathToAbsoluteRootPath(self, path):
        '''
        Converts the given path to an absolute path  for the root directory.
        The result has to be usable to access the corresponding file in the
        root directory.
        '''
    
    @abstractmethod
    def __processReadDirEntry(self, absRootPath, entry):
        '''
        Returns the view entries that shall be displayed for the given entry
        '''  

    def access(self, path, mode):
        if mode & os.W_OK != 0 or not os.access(self.__convertViewPathToAbsoluteRootPath(path), mode):
            raise FuseOSError(EPERM)

    def chmod(self, path, mode):
        raise FuseOSError(EPERM)

    def chown(self, path, uid, gid):
        raise FuseOSError(EPERM)

    def create(self, path, mode):
        raise FuseOSError(EPERM)

    def flush(self, path, fh):
        # we do not support writing, so we ignore this call
        return

    def fsync(self, path, datasync, fh):
        # we do not support writing, so we ignore this call
        return

    @abstractmethod
    def getattr(self, path, fh=None):
        """
        Returns the attributes for the given path.
        """
        
    getxattr = None

    def link(self, target, source):
        raise FuseOSError(EPERM)

    listxattr = None
    
    def mknod(self, path, mode, dev):
        raise FuseOSError(EPERM)
    
    def mkdir(self, path, mode):
        raise FuseOSError(EPERM)

    def open(self, path, flags):
        if flags & (os.O_CREAT | os.O_APPEND | os.O_RDWR | os.O_WRONLY) != 0:
            raise FuseOSError(EPERM)
        absRootPath = self.__convertViewPathToAbsoluteRootPath(path)
        if os.path.isdir(absRootPath):
            return 0
        try:
            return self.fileHandleContainer.registerHandle(absRootPath, flags)
        except ValueError:
            raise FuseOSError(ENOENT)

    @abstractmethod
    def read(self, path, size, offset, fh):
        '''
        Returns the requested file content for the view.
        '''
        
    def readdir(self, path, fh):
        dirContent = ['.', '..']
        absRootPath = self.__convertViewPathToAbsoluteRootPath(path)
        for entry in os.listdir(absRootPath):
            dirContent.extend(self.__processReadDirEntry(absRootPath, entry))
        return dirContent       

    def readlink(self, path, buf, bufsize):
        raise FuseOSError(EPERM)

    def release(self, path, fh):
        try:
            self.fileHandleContainer.unregisterHandle(fh)
        except ValueError:
            raise FuseOSError(ENOENT)

    def rename(self, old, new):
        raise FuseOSError(EPERM)
    
    def rmdir(self, path):
        raise FuseOSError(EPERM)

    def statfs(self, path):
        # TODO: We should adjust these data...
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def symlink(self, target, source):
        raise FuseOSError(EPERM)

    def truncate(self, path, length, fh=None):
        raise FuseOSError(EPERM)

    def unlink(self, path):
        raise FuseOSError(EPERM)

    def utimens(self, path, timestruct):
        raise FuseOSError(EPERM)

    def write(self, path, data, offset, fh):
        raise FuseOSError(EPERM)
    
    def __getAbsolutePath(self, path):
        absRootPath = self.root + path
        if os.path.islink(absRootPath):
            return os.path.realpath(absRootPath)
        return absRootPath
