import os, unittest
from encviewfuse.encryption.extensions.NameFileSaltProvider import NameFileSaltProvider
from encviewfuse.test.ecryption.extensions.SaltProviderTestBase import SaltProviderBaseTest

class NameFilenameSaltProviderTest(SaltProviderBaseTest, unittest.TestCase):

    def constructSubject(self):
        return NameFileSaltProvider()
    
    def getId(self):
        return 'filename'

    def testGivenSaltForFile(self):
        tmpFile = os.path.join(self.tmpDir, 'afile')
        open(tmpFile, 'a').close()
        salt = self.subject.getSaltFor(tmpFile)
        self.assertEqual('afile', salt)

    def testDirectoryPath(self):
        tmpDir = os.path.join(self.tmpDir, 'adir')
        os.mkdir(tmpDir)
        with self.assertRaises(ValueError) as _:
            self.subject.getSaltFor(tmpDir)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()