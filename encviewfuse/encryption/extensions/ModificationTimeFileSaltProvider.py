import os
from encviewfuse.encryption.EncryptionExtensions import FileSaltProvider

class ModificationTimeFileSaltProvider(FileSaltProvider):
    
    def getId(self):
        return "mtime"
    
    def getSaltFor(self, absoluteFilePath):
        if not os.path.exists(absoluteFilePath):
            raise ValueError("The given path must exist.")
        if not os.path.isfile(absoluteFilePath):
            raise ValueError("The given path must be a file path.")
        return str(os.path.getmtime(absoluteFilePath))
        