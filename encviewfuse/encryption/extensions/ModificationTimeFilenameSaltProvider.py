import os
from encviewfuse.encryption.EncryptionExtensions import FilenameSaltProvider

class ModificationTimeFilenameSaltProvider(FilenameSaltProvider):
    
    def getId(self):
        return "mtime"
    
    def getSaltFor(self, absoluteFilePath):
        if not os.path.exists(absoluteFilePath):
            raise ValueError("The given path must exist.")
        if os.path.isdir(absoluteFilePath):
            return os.path.basename(absoluteFilePath)
        return str(os.path.getmtime(absoluteFilePath))
        