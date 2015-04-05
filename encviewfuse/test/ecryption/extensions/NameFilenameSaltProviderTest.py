import os, unittest
from encviewfuse.encryption.extensions.NameFilenameSaltProvider import NameFilenameSaltProvider
from encviewfuse.test.ecryption.extensions.SaltProviderTestBase import SaltProviderBaseTest

class NameFilenameSaltProviderTest(SaltProviderBaseTest, unittest.TestCase):

    def constructSubject(self):
        return NameFilenameSaltProvider()
        
    def getId(self):
        return 'filename'

    def testGivenSaltForFile(self):
        tmpFile = os.path.join(self.tmpDir, 'afile')
        open(tmpFile, 'a').close()
        salt = self.subject.getSaltFor(tmpFile)
        self.assertEqual('afile', salt)
        
    def testGivenSaltForDirectory(self):
        tmpDir = os.path.join(self.tmpDir, 'adir')
        os.mkdir(tmpDir)
        salt = self.subject.getSaltFor(tmpDir)
        self.assertEqual('adir', salt)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()