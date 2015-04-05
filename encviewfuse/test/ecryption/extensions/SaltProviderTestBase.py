from tempfile import mkdtemp, mktemp

import shutil
from abc import abstractmethod, ABCMeta

class SaltProviderBaseTest(object, metaclass=ABCMeta):
    
    def setUp(self):
        self.tmpDir = mkdtemp()
        self.subject = self.constructSubject()
        self.id = self.getId()
        
    @abstractmethod
    def constructSubject(self):
        '''
        Returns an instance of a test subject.
        '''
        
    @abstractmethod
    def getId(self):
        '''
        Returns the id of the salt provider.
        '''
        
    def tearDown(self):
        shutil.rmtree(self.tmpDir)

    def testGetId(self):
        self.assertEqual(self.id, self.subject.getId())

    def testNotExistingPath(self):
        notExistingPath = mktemp()
        with self.assertRaises(ValueError) as _:
            self.subject.getSaltFor(notExistingPath)
