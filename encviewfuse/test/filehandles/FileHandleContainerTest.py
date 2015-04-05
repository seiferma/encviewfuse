import unittest
from encviewfuse.filehandles.FileHandleContainer import FileHandleContainer
import tempfile
import shutil
import os


class FileHandleContainerTest(unittest.TestCase):

    def setUp(self):
        self.subject = FileHandleContainer()
        self.tmpdir = tempfile.mkdtemp()
        self.files = list()
        for _ in range(0,10):
            self.files.append(tempfile.NamedTemporaryFile(dir=self.tmpdir, delete=False).name)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        
    def testRegisterAndUnregisterFile(self):
        fd = self.subject.registerHandle(self.files[0], os.O_RDONLY)
        self.assertTrue(fd > 0, "File handle is invalid.")
        
        vf = self.subject.getHandle(fd)
        self.assertEqual(self.files[0], vf.name())
        
        self.subject.unregisterHandle(fd)
        
    def testRegisterAndUnregisterMultipleFiles(self):
        fds = list()
        
        for i in range(0,len(self.files)):
            fd = self.subject.registerHandle(self.files[i], os.O_RDONLY)
            self.assertTrue(fd > 0, "File handle is invalid.")
            fds.append(fd)

        for i in range(0,len(self.files)):
            vf = self.subject.getHandle(fds[i])
            self.assertEqual(self.files[i], vf.name())
            
        for _ in range(len(self.files),0):
            self.subject.unregisterHandle(fds[i])

    def testRegisterNotExistingFile(self):
        notExistingFile = tempfile.mktemp()
        with self.assertRaises(ValueError) as _:
            self.subject.registerHandle(notExistingFile, os.O_RDONLY)

    def testGetInvalidHandle(self):
        with self.assertRaises(ValueError) as _:
            self.subject.getHandle(1)

    def testUnregisterInvalidHandle(self):
        with self.assertRaises(ValueError) as _:
            self.subject.unregisterHandle(1)
            
    def testUnregisterSpecialHandle(self):
        self.subject.unregisterHandle(0)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()