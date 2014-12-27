from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser, ArgumentTypeError, Action
from encviewfuse.encryption.Encryption import Encryption
from errno import EACCES, EPERM
from fuse import FuseOSError, Operations, LoggingMixIn
import os


class EncryptedViewFuseBase(LoggingMixIn, Operations, metaclass=ABCMeta):
    
    def __init__(self, root, secret, maxFileSize, fileHandleContainer):
        self.root = os.path.realpath(root)
        self.encryption = Encryption(secret)
        self.maxFileSize = maxFileSize
        self.fileHandleContainer = fileHandleContainer

    def __call__(self, op, path, *args):
        return super(EncryptedViewFuseBase, self).__call__(op, path, *args)

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
        
    @abstractmethod
    def __isViewPathAccessible(self, path, mode):
        '''
        Indicates whether the given view path is accessiable with the given mode
        '''
    
    
        
        

    def access(self, path, mode):
        if mode is os.W_OK or not self.__isViewPathAccessible(path, mode):
            raise FuseOSError(EACCES)

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
        return self.fileHandleContainer.registerHandle(path)

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
        self.fileHandleContainer.unregisterHandle(fh)

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

    utimens = os.utime

    def write(self, path, data, offset, fh):
        raise FuseOSError(EPERM)






class FullPaths(Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))
     
def __is_dir(dirname):
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise ArgumentTypeError(msg)
    else:
        return dirname 

def parseArguments():
    parser = ArgumentParser(description='Encrypted file system for large cloud backups')
    parser.add_argument('-s', '--secret', type=str, required=True, dest='secretKey', help="the secret for the encryption")
    parser.add_argument('-ms', '--maximum-file-size', type=int, default=None, dest='maxFileSize', help="the maximum file size of a single file in bytes.")
    parser.add_argument('rootdir', action=FullPaths, type=__is_dir, help='the document root for the original files')
    parser.add_argument('mountpoint', action=FullPaths, type=__is_dir, help='the mount point')
    return parser.parse_args()

