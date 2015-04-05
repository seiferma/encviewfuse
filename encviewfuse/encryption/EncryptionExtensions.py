from abc import ABCMeta, abstractmethod

class SaltProvider(object, metaclass=ABCMeta):

    @abstractmethod
    def getId(self):
        '''
        Returns the unique id of the extension that can
        be used to activate it via a command line option.
        '''

    @abstractmethod
    def getSaltFor(self, absoluteFilePath):
        '''
        Calculates the salt for the file name encryption
        based on the given absolute file path.
        '''

class FilenameSaltProvider(SaltProvider):
    pass

class FileSaltProvider(SaltProvider):
    pass