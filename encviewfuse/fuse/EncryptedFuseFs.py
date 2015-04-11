from deterministic_encryption_utils.encryption.Encryption import MalformedInputException
from encviewfuse.fuse._FuseFsBase import FuseFsBase
from fuse import FUSE, FuseOSError
from errno import ENOENT
import os, stat, sys
from encviewfuse.fuse._ArgumentParser import FuseArgumentParser,\
    ArgumentParserError
from deterministic_encryption_utils.encryption.extensions.ExtensionRegistry import ExtensionRegistry
from argparse import ArgumentTypeError


class EncViewFuse(FuseFsBase):
    
    def __init__(self, root, secret, fileSaltProvider, filenameSaltProvider):
        super(EncViewFuse, self).__init__(root, secret, fileSaltProvider, filenameSaltProvider)

    def read(self, path, size, offset, fh):
        try:
            virtualFile = self.fileHandleContainer.getHandle(fh)
        except ValueError:
            raise FuseOSError(ENOENT)
        return self.encryption.encryptedContent(virtualFile, offset, size)
    
    def getattr(self, path, fh=None):
        try:
            absRootPath = self.__decryptToAbsolutePath(path)
            
            if not os.path.exists(absRootPath) or os.path.islink(absRootPath):
                raise FuseOSError(ENOENT)
            
            st = os.lstat(absRootPath)
            stats = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
            stats['st_mode'] = st.st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            
            if os.path.isfile(absRootPath):
                stats['st_size'] = self.__encryptedFileSize(os.path.getsize(absRootPath))                
            return stats
        except MalformedInputException:
            raise FuseOSError(ENOENT)


    def _FuseFsBase__convertViewPathToAbsoluteRootPath(self, path):
        return self.__decryptToAbsolutePath(path)

    def _FuseFsBase__processReadDirEntry(self, absRootPath, entry):
        absRootPathEntry = os.path.join(absRootPath, entry)
        entryViewName = self.encryption.encryptFileName(absRootPathEntry, entry)
        return [entryViewName]
        
    def __decryptToAbsolutePath(self, path):
        return os.path.realpath(self.root + self.encryption.decryptPath(path))
    
    def __encryptedFileSize(self, fileSizeInBytes):
        return self.encryption.encryptedFileSize(fileSizeInBytes)
    



def main():
    args = None
    try:
        args = FuseArgumentParser(ExtensionRegistry()).parseArguments(sys.argv[1:])
    except (ArgumentTypeError, ArgumentParserError) as e:
        print('Error during command line parsing: {0}'.format(str(e)))
        sys.exit(1)
    
    FUSE(EncViewFuse(args.device, args.mountOptions.secret, args.mountOptions.fileSalt, args.mountOptions.filenameSalt), args.dir, **args.mountOptions.others)

if __name__ == '__main__':
    main()
