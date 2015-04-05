from encviewfuse.encryption.EncryptionExtensions import FileSaltProvider, FilenameSaltProvider
from encviewfuse.encryption.extensions import * # Necessary for finding subclasses

class ExtensionRegistry(object):
    
    def __init__(self):
        self.fileSaltProviders = ExtensionRegistry.__getProviders(FileSaltProvider)
        self.filenameSaltProviders = ExtensionRegistry.__getProviders(FilenameSaltProvider)
    
    def getFileSaltProvider(self, identifier):
        if identifier not in self.fileSaltProviders.keys():
            raise ValueError("The given identifier is invalid.")
        return self.fileSaltProviders.get(identifier)
    
    def getFileSaltProviderIds(self):
        return self.fileSaltProviders.keys()
    
    def getFilenameSaltProvider(self, identifier):
        if identifier not in self.filenameSaltProviders.keys():
            raise ValueError("The given identifier is invalid.")
        return self.filenameSaltProviders.get(identifier)
    
    def getFilenameSaltProviderIds(self):
        return self.filenameSaltProviders.keys()
    
    @staticmethod
    def __getProviders(cls):
        providers = dict()
        for c in ExtensionRegistry.__findAllSubclasses(cls):
            provider = c()
            providers[provider.getId()] = provider
        return providers 
    
    @staticmethod
    def __findAllSubclasses(cls):
        subclasses = set()
        for s in cls.__subclasses__():
            subclasses.add(s)
            for g in ExtensionRegistry.__findAllSubclasses(s):
                subclasses.add(g)
        return subclasses
