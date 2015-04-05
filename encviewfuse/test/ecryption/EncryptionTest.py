import unittest,os
from encviewfuse.encryption.Encryption import Encryption, EncryptionException
import tempfile
import shutil
from encviewfuse.filehandles.VirtualFile import VirtualFile

class EncryptionTest(unittest.TestCase):

    class _SaltProviderMock(object):
        def getSaltFor(self, absoluteFilePath):
            if not os.path.exists(absoluteFilePath):
                raise ValueError('The given path {0} cannot be used to determine a salt.'.format(absoluteFilePath))
            return '42'

    def setUp(self):
        saltProviderMock = EncryptionTest._SaltProviderMock()
        self.subject = Encryption('abc', saltProviderMock, saltProviderMock)

    def testEncryptAndDecryptFilename(self):
        tmpFile = tempfile.NamedTemporaryFile()
        rootPath = tmpFile.name
        encryptedFileName = self.subject.encryptFileName(rootPath, os.path.basename(rootPath))
        self.assertEqual(os.path.basename(rootPath), self.subject.decryptFileName(encryptedFileName))
        
    def testErrorOnEncryptingNotAbsoluteFilePath(self):
        with self.assertRaises(EncryptionException) as _:
            self.subject.encryptFileName(tempfile.mktemp(), 'abc123')
        
    def testEncryptAndDecryptFilenameWithUnicode(self):
        tmpFile = tempfile.NamedTemporaryFile(prefix='ÄÖÜ')
        rootPath = tmpFile.name
        encryptedFileName = self.subject.encryptFileName(rootPath, os.path.basename(rootPath))
        self.assertEqual(os.path.basename(rootPath), self.subject.decryptFileName(encryptedFileName))
        
    def testEncryptAndDecryptPath(self):
        rootDir = tempfile.mkdtemp()
        aFolder = tempfile.mkdtemp(dir=rootDir)
        aFile = tempfile.NamedTemporaryFile(dir=aFolder, delete=False)
        path = aFile.name[len(rootDir):]
        
        try:
            encryptedPath = self.subject.encryptPath(rootDir, path)
            self.assertEqual(len(os.path.split(path)), len(os.path.split(encryptedPath)))
            self.assertEqual(path, self.subject.decryptPath(encryptedPath))
        finally:
            shutil.rmtree(rootDir)
            
    def testEncryptAndDecryptPathWithSymlinks(self):
        rootDir = tempfile.mkdtemp()
        aFolder = tempfile.mkdtemp(dir=rootDir)
        aFile = tempfile.NamedTemporaryFile(dir=aFolder, delete=False)
        symLink = tempfile.mktemp(dir=aFolder)
        os.link(aFile.name, symLink)
        path = symLink[len(rootDir):]
        
        try:
            encryptedPath = self.subject.encryptPath(rootDir, path)
            self.assertEqual(len(os.path.split(path)), len(os.path.split(encryptedPath)))
            self.assertEqual(path, self.subject.decryptPath(encryptedPath))
        finally:
            shutil.rmtree(rootDir)
        
    def testEncryptAndDecryptContent(self):
        plainFile = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        encryptedFile = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
        
        try:
            # fill plain text file
            with plainFile as f:
                f.write('abc')
            plainFileVirtual = VirtualFile(plainFile.name)
            
            # fill encrypted file
            encryptedContent = self.subject.encryptedContent(plainFileVirtual, 0, 4096)
            with encryptedFile as f:
                f.write(encryptedContent)
            
            # ensure that encrypted file size matches the real size
            self.assertEqual(os.path.getsize(encryptedFile.name), self.subject.encryptedFileSize(os.path.getsize(plainFile.name)))
            
            # ensure that decrypted file size matches the real size
            encryptedFileVirtual= VirtualFile(encryptedFile.name)
            self.assertEqual(os.path.getsize(plainFile.name), self.subject.decryptedFileSize(encryptedFileVirtual))
            
            # decrypt content and compare to plaintext
            decryptedContent = self.subject.decryptedContent(encryptedFileVirtual, 0, 4096)
            self.assertEqual('abc', decryptedContent.decode())            
        finally:
            os.remove(plainFile.name)
            os.remove(encryptedFile.name)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'EncryptionTest.testName']
    unittest.main()