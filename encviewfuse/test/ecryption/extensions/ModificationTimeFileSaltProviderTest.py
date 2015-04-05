import os, unittest

from encviewfuse.encryption.extensions.ModificationTimeFileSaltProvider import ModificationTimeFileSaltProvider
from encviewfuse.test.ecryption.extensions.SaltProviderTestBase import SaltProviderBaseTest

class ModificationTimeFileSaltProviderTest(SaltProviderBaseTest, unittest.TestCase):

    def constructSubject(self):
        return ModificationTimeFileSaltProvider()
    
    def getId(self):
        return 'mtime'

    def testGivenSaltForFile(self):
        tmpFile = os.path.join(self.tmpDir, 'afile')
        open(tmpFile, 'a').close()
        salt = self.subject.getSaltFor(tmpFile)
        self.assertEqual(str(os.path.getmtime(tmpFile)), salt)

    def testDirectoryPath(self):
        tmpDir = os.path.join(self.tmpDir, 'adir')
        os.mkdir(tmpDir)
        with self.assertRaises(ValueError) as _:
            self.subject.getSaltFor(tmpDir)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()