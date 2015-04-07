import os, shutil, tempfile, unittest
from encviewfuse.fuse._ArgumentParser import FuseArgumentParser, ArgumentParserError
from argparse import ArgumentTypeError

class TestFuseArgumentParser(unittest.TestCase):

    class _ExtensionRegistryMock(object):
        
        FILE_SALT_PROVIDERS = ['f0', 'f1', 'f2']
        FILENAME_SALT_PROVIDERS = ['fn0', 'fn1', 'fn2']
        
        def getFileSaltProvider(self, identifier):
            if identifier not in TestFuseArgumentParser._ExtensionRegistryMock.FILE_SALT_PROVIDERS:
                raise ValueError()
            return identifier
    
        def getFileSaltProviderIds(self):
            return TestFuseArgumentParser._ExtensionRegistryMock.FILE_SALT_PROVIDERS
        
        def getFilenameSaltProvider(self, identifier):
            if identifier not in TestFuseArgumentParser._ExtensionRegistryMock.FILENAME_SALT_PROVIDERS:
                raise ValueError()
            return identifier
        
        def getFilenameSaltProviderIds(self):
            return TestFuseArgumentParser._ExtensionRegistryMock.FILENAME_SALT_PROVIDERS


    def setUp(self):
        self.subject = FuseArgumentParser(TestFuseArgumentParser._ExtensionRegistryMock())
        self.tmpDir1 = tempfile.mkdtemp()
        self.tmpDir2 = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.tmpDir1)
        shutil.rmtree(self.tmpDir2)

    def testErrorNoArgument(self):
        with self.assertRaises(ArgumentParserError) as _:
            self.subject.parseArguments([])
            
    def testErrorNotExistingMountDir(self):
        notExistingDirectory = tempfile.mktemp()
        with self.assertRaises(ArgumentParserError) as _:
            self.subject.parseArguments([notExistingDirectory, self.tmpDir1, '-o', 'abc'])
            
    def testErrorNotExistingRootDir(self):
        notExistingDirectory = tempfile.mktemp()
        with self.assertRaises(ArgumentParserError) as _:
            self.subject.parseArguments([self.tmpDir1, notExistingDirectory, '-o', 'abc'])
            
    def testErrorNotExistingMountOptions(self):
        with self.assertRaises(ArgumentParserError) as _:
            self.subject.parseArguments([self.tmpDir1, self.tmpDir2])
            
    def testErrorEmptyMountOptions(self):
        with self.assertRaises(ArgumentParserError) as _:
            self.subject.parseArguments([self.tmpDir1, self.tmpDir2, '-o'])
            
    def testValidMountOptions(self):
        args = self.subject.parseArguments([self.tmpDir1, self.tmpDir2, '-o', 'secret=123,fileSalt=f0,filenameSalt=fn0,allow_other,qq=15'])
        self.assertEqual('123', args.mountOptions.secret)
        self.assertEqual('f0', args.mountOptions.fileSalt)
        self.assertEqual('fn0', args.mountOptions.filenameSalt)
        self.assertIsInstance(args.mountOptions.others, dict)
        expectedOtherOptions = dict()
        expectedOtherOptions['allow_other'] = True
        expectedOtherOptions['qq'] = '15'
        self.assertDictContainsSubset(expectedOtherOptions, args.mountOptions.others)
        
    def testErrorInvalidFileSaltProvider(self):
        with self.assertRaises(ArgumentTypeError) as _:
            self.subject.parseArguments([self.tmpDir1, self.tmpDir2, '-o', 'secret=123,fileSalt=f3,filenameSalt=fn0'])
            
    def testErrorInvalidFilenameSaltProvider(self):
        with self.assertRaises(ArgumentTypeError) as _:
            self.subject.parseArguments([self.tmpDir1, self.tmpDir2, '-o', 'secret=123,fileSalt=f0,filenameSalt=fn3'])
            
    def testErrorEmptySecret(self):
        with self.assertRaises(ArgumentParserError) as _:
            self.subject.parseArguments([self.tmpDir1, self.tmpDir2, '-o', 'secret=,fileSalt=f0,filenameSalt=fn0'])
            
    def testErrorNoSecret(self):
        with self.assertRaises(ArgumentTypeError) as _:
            self.subject.parseArguments([self.tmpDir1, self.tmpDir2, '-o', 'fileSalt=f0,filenameSalt=fn0'])
            
    def testErrorInvalidSecretFile(self):
        with self.assertRaises(ArgumentTypeError) as _:
            nonExistingFile = tempfile.mktemp()
            self.subject.parseArguments([self.tmpDir1, self.tmpDir2, '-o', 'secretfile={0},fileSalt=f0,filenameSalt=fn0'.format(nonExistingFile)])
            
    def testValidMountOptionsWithSecretFile(self):
        secretFile = tempfile.NamedTemporaryFile(mode='w+',delete=False)
        secretFile.write('abc')
        secretFile.flush()
        try:
            args = self.subject.parseArguments([self.tmpDir1, self.tmpDir2, '-o', 'secretfile={0},fileSalt=f0,filenameSalt=fn0'.format(secretFile.name)])
            self.assertEqual('abc', args.mountOptions.secret)
        finally:
            os.remove(secretFile.name)

        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()