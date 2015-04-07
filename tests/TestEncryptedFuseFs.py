import os, shutil, tempfile, unittest
from encviewfuse.fuse.EncryptedFuseFs import EncViewFuse
from encviewfuse.encryption.Encryption import Encryption
from collections import namedtuple
import stat
from fuse import FuseOSError
from encviewfuse.encryption.VirtualFile import VirtualFile


class TestEncryptedFuseFs(unittest.TestCase):

    class _SaltProviderMock(object):
        def getSaltFor(self, absoluteFilePath):
            return '42'

    def setUp(self):
        self.rootDir = tempfile.mkdtemp()
        self.dirStructure = TestEncryptedFuseFs.__setupRootDir(self.rootDir)
        saltProvider = TestEncryptedFuseFs._SaltProviderMock()
        self.subject = EncViewFuse(self.rootDir, 'abc', saltProvider, saltProvider)
        self.encryption = Encryption('abc', saltProvider, saltProvider)
        
        
    @staticmethod
    def __setupRootDir(rootDir):
        # RootDir
        # - f1
        # - d1
        #   - f2
        # - d2
        #   - fl1 (--> f2)
        # - dl1 (--> d2)
        resultObject = namedtuple('DirStructure', ['rootDir', 'f1', 'f2', 'd1', 'd2', 'fl1', 'dl1'])
        resultObject.rootDir = rootDir
        resultObject.f1 = TestEncryptedFuseFs.__createFileWithRandomContent(rootDir, 7)
        resultObject.d1 = tempfile.mkdtemp(dir=rootDir)
        resultObject.d2 = tempfile.mkdtemp(dir=rootDir)
        resultObject.f2 = TestEncryptedFuseFs.__createFileWithRandomContent(resultObject.d1, 15)
        resultObject.fl1 = tempfile.mktemp(dir=resultObject.d2)
        os.symlink(resultObject.f2, resultObject.fl1)
        resultObject.dl1 = tempfile.mktemp(dir=rootDir)
        os.symlink(resultObject.d2, resultObject.dl1)
        return resultObject
        
    
    @staticmethod
    def __createFileWithRandomContent(path, size):
        file = tempfile.NamedTemporaryFile(dir=path, delete=False)
        with file as f:
            f.write(os.urandom(size))
        return file.name

    def tearDown(self):
        shutil.rmtree(self.rootDir)


    def testReadDirRoot(self):
        result = self.subject.readdir('/', None)
         
        self.assertIn('.', result)
        result.remove('.')
        self.assertIn('..', result)
        result.remove('..')
         
        self.assertEqual(len(os.listdir(self.rootDir)), len(result))
        for filename in os.listdir(self.rootDir):
            self.assertIn(self.__getEncryptedFileName(os.path.join(self.rootDir, filename)), result)
        
    def testReadDirSubdir(self):
        self.__testReadDir(self.dirStructure.d2)
        
    def testReadDirSubdirLink(self):
        self.__testReadDir(self.dirStructure.dl1)
            
    def testAccessRead(self):
        filePath = self.dirStructure.f2
        filePathEncrypted =  self.__getEncryptedFilePath(filePath)
        
        self.assertIsNone(self.subject.access(filePathEncrypted, os.R_OK), "No return value is expected if access is granted.")
        
    def testAccessWrite(self):
        filePath = self.dirStructure.f2
        filePathEncrypted =  self.__getEncryptedFilePath(filePath)
        
        with self.assertRaises(FuseOSError) as _:
            self.subject.access(filePathEncrypted, os.W_OK)
        
    def testAccessReadWrite(self):
        filePath = self.dirStructure.f2
        filePathEncrypted =  self.__getEncryptedFilePath(filePath)
        
        with self.assertRaises(FuseOSError) as _:
            self.subject.access(filePathEncrypted, os.W_OK | os.R_OK)
        
    def testGetAttrFile(self):
        filePath = self.dirStructure.f2
        attrs = os.lstat(filePath)
        
        filePathEncrypted =  self.__getEncryptedFilePath(filePath)
        encryptedAttrs = self.subject.getattr(filePathEncrypted)
        
        self.__assertEqualsStats(attrs, encryptedAttrs)
    
    def testGetAttrFileLink(self):
        filePath = self.dirStructure.fl1
        attrs = os.lstat(os.path.realpath(filePath))
        
        filePathEncrypted =  self.__getEncryptedFilePath(filePath)
        encryptedAttrs = self.subject.getattr(filePathEncrypted)
        
        self.__assertEqualsStats(attrs, encryptedAttrs)
        
    def testGetAttrDir(self):
        filePath = self.dirStructure.d1
        attrs = os.lstat(filePath)
        
        filePathEncrypted =  self.__getEncryptedFilePath(filePath)
        encryptedAttrs = self.subject.getattr(filePathEncrypted)
        
        self.__assertEqualsStats(attrs, encryptedAttrs, True)
        
    def testGetAttrDirLink(self):
        filePath = self.dirStructure.dl1
        attrs = os.lstat(os.path.realpath(filePath))
        
        filePathEncrypted =  self.__getEncryptedFilePath(filePath)
        encryptedAttrs = self.subject.getattr(filePathEncrypted)
        
        self.__assertEqualsStats(attrs, encryptedAttrs, True)
        
    def testGetAttrFileLinkInDirLink(self):
        filePath = os.path.join(self.dirStructure.dl1, os.path.basename(self.dirStructure.fl1))
        attrs = os.lstat(os.path.realpath(filePath))
        
        filePathEncrypted =  self.__getEncryptedFilePath(filePath)
        encryptedAttrs = self.subject.getattr(filePathEncrypted)
        
        self.__assertEqualsStats(attrs, encryptedAttrs)
    
    def testOpenRelease(self):
        filePath = self.dirStructure.f2
        encryptedFilePath = self.__getEncryptedFilePath(filePath)
        fd = self.subject.open(encryptedFilePath, os.O_RDONLY)
        self.subject.release(encryptedFilePath, fd)
        
    def testOpenReleaseFileLink(self):
        filePath = self.dirStructure.fl1
        encryptedFilePath = self.__getEncryptedFilePath(filePath)
        fd = self.subject.open(encryptedFilePath, os.O_RDONLY)
        self.subject.release(encryptedFilePath, fd)
        
    def testOpenDirectory(self):
        filePath = self.dirStructure.d1
        encryptedFilePath = self.__getEncryptedFilePath(filePath)
        self.assertEqual(0, self.subject.open(encryptedFilePath, os.O_RDONLY))
        
    def testOpenDirectoryLink(self):
        filePath = self.dirStructure.dl1
        encryptedFilePath = self.__getEncryptedFilePath(filePath)
        self.assertEqual(0, self.subject.open(encryptedFilePath, os.O_RDONLY))
        
    def testOpenFileWriting(self):
        filePath = self.dirStructure.f2
        encryptedFilePath = self.__getEncryptedFilePath(filePath)
        with self.assertRaises(FuseOSError) as _:
            self.subject.open(encryptedFilePath, os.O_WRONLY)
            
    def testOpenFileAppending(self):
        filePath = self.dirStructure.f2
        encryptedFilePath = self.__getEncryptedFilePath(filePath)
        with self.assertRaises(FuseOSError) as _:
            self.subject.open(encryptedFilePath, os.O_APPEND)
    
    def testReadFile(self):
        self.__testReadFile(self.dirStructure.f2)
    
    def testReadFileLink(self):
        self.__testReadFile(self.dirStructure.fl1)

    def testReadFileLinkInDirectoryLink(self):
        filePath = os.path.join(self.dirStructure.dl1, os.path.basename(self.dirStructure.fl1))
        self.__testReadFile(filePath)
        
    
    def __getEncryptedFileName(self, absPath):
        return self.encryption.encryptFileName(absPath, os.path.basename(absPath))
    
    def __getEncryptedFilePath(self, absPath):
        relativePath = absPath[len(self.rootDir):]
        return self.encryption.encryptPath(self.rootDir, relativePath)

    def __testReadDir(self, absolutePath):
        dirPath = absolutePath
        dirNameEncrypted = self.__getEncryptedFileName(dirPath)
        
        result = self.subject.readdir('/{0}'.format(dirNameEncrypted), None)
        
        self.assertIn('.', result)
        result.remove('.')
        self.assertIn('..', result)
        result.remove('..')
        
        self.assertEqual(len(os.listdir(dirPath)), len(result))
        for filename in os.listdir(dirPath):
            self.assertIn(self.__getEncryptedFileName(os.path.join(dirPath, filename)), result)

    def __testReadFile(self, absolutePath):
        filePath = absolutePath
        encryptedFilePath = self.__getEncryptedFilePath(filePath)
        fd = self.subject.open(encryptedFilePath, os.O_RDONLY)
        encryptedContent = self.subject.read(None, 4096, 0, fd)
        self.subject.release(None, fd)
        
        encryptedFile = tempfile.NamedTemporaryFile(delete=False)
        try:
            with encryptedFile as f:
                f.write(encryptedContent)
                
            f = VirtualFile(encryptedFile.name , os.O_RDONLY)
            decryptedContent = self.encryption.decryptedContent(f, 0, 4096)
            
            expectedContent = None
            with open(os.path.realpath(filePath), 'rb') as q:
                expectedContent = q.read()
                
            self.assertEqual(expectedContent, decryptedContent)
        finally:
            os.remove(encryptedFile.name)

    def __assertEqualsStats(self, expected, actual, directory=False):
        self.assertEqual(expected.st_atime, actual['st_atime'])
        self.assertEqual(expected.st_ctime, actual['st_ctime'])
        self.assertEqual(expected.st_gid, actual['st_gid'])
        self.assertEqual(expected.st_mtime, actual['st_mtime'])
        self.assertEqual(expected.st_uid, actual['st_uid'])
        self.assertEqual(expected.st_nlink, actual['st_nlink'])
        self.assertEqual(expected.st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH), actual['st_mode'])
        if directory:
            self.assertEqual(expected.st_size, actual['st_size'])
        else:
            self.assertEqual(Encryption.FILE_KEYADDITION_LENGTH + (expected.st_size // Encryption.BLOCKSIZE_BYTES + 1) * Encryption.BLOCKSIZE_BYTES, actual['st_size'])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()