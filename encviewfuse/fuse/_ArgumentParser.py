import os
from collections import namedtuple
from argparse import ArgumentTypeError, ArgumentParser, Action
from abc import abstractmethod, ABCMeta

class ArgumentParserError(Exception): pass

class FuseArgumentParser(object):
    
    def __init__(self, extensionRegistry, saltProvidersRequired=True):
        self.extensionRegistry = extensionRegistry
        self.saltProvidersRequired = saltProvidersRequired

    class __ThrowingArgumentParser(ArgumentParser):
        def error(self, message):
            raise ArgumentParserError(message)
    
    def parseArguments(self, arguments):
        parser = FuseArgumentParser.__ThrowingArgumentParser(description='Encrypted file system for large cloud backups')
        parser.add_argument('device', action=_FullPaths, type=FuseArgumentParser.__is_dir, help='the document root for the original files')
        parser.add_argument('dir', action=_FullPaths, type=FuseArgumentParser.__is_dir, help='the mount point')
        parser.add_argument("-o", action=FuseArgumentParser.__makeMountOptionsAction(self.extensionRegistry, self.saltProvidersRequired), type=FuseArgumentParser.__are_mount_options, required=True, dest='mountOptions', help='mount options')
        return parser.parse_args(arguments)
    
    @staticmethod
    def __is_dir(dirname):
        """Checks if a path is an actual directory"""
        if not os.path.isdir(dirname):
            msg = "{0} is not a directory".format(dirname)
            raise ArgumentTypeError(msg)
        else:
            return dirname
    
    @staticmethod
    def __are_mount_options(options):
        optionList = options.split(',')
        
        for option in optionList:
            if not option:
                raise ArgumentTypeError('Empty options in the mount options are not allowed (check your commas).')
            keyValuePair = option.split('=')
            if len(keyValuePair) > 2:
                raise ArgumentTypeError('The option "{0}" is considered a key-value pair but consists of more then 2 parts.'.format(option))
            if len(keyValuePair) == 2:
                if not keyValuePair[0]:
                    raise ArgumentTypeError('The key part of the key-value pair "{0}" must not be empty.'.format(option))
                if not keyValuePair[1]:
                    raise ArgumentTypeError('The value part of the key-value pair "{0}" must not be empty.'.format(option))
    
        return options
    
    @staticmethod
    def __makeMountOptionsAction(extensionRegistry, saltProvidersRequired):
        class customAction(_MountOptions):
            def getFileSaltIds(self):
                return extensionRegistry.getFileSaltProviderIds()
                        
            def getFilenameSaltIds(self):
                return extensionRegistry.getFilenameSaltProviderIds()
            
            def getFileSaltProvider(self, identifier):
                return extensionRegistry.getFileSaltProvider(identifier)
            
            def getFilenameSaltProvider(self, identifier):
                return extensionRegistry.getFilenameSaltProvider(identifier)
            
            def getSaltProvidersRequired(self):
                return saltProvidersRequired
            
        return customAction


class _FullPaths(Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))
        
class _MountOptions(Action, metaclass=ABCMeta):
    
    def __call__(self, parser, namespace, values, option_string=None):
        resultObject = namedtuple('ParsedMountOptions', ['secret', 'fileSalt', 'filenameSalt', 'others'])
        options = values.split(',')
                
        resultObject.secret = self.getSecretFromOptions(options)
        
        if self.getSaltProvidersRequired():
            try:
                resultObject.fileSalt = self.getFileSaltProvider(self.getValueForKey(options, "fileSalt"))
            except ValueError:
                raise ArgumentTypeError('The file salt provider is invalid.')
            try:
                resultObject.filenameSalt = self.getFilenameSaltProvider(self.getValueForKey(options, "filenameSalt"))
            except ValueError:
                raise ArgumentTypeError('The filename salt provider is invalid.')
        
        interestingOptions = ["secret=", "secretfile=", "fileSalt", "filenameSalt"]
        filteredOptions = filter(lambda x: not any(x.startswith(string) for string in interestingOptions), options)
        otherOptions = dict()
        for option in filteredOptions:
            parts = option.split('=')
            if len(parts) == 1:
                otherOptions[parts[0]] = True
            else:
                otherOptions[parts[0]] = parts[1]
        resultObject.others = otherOptions

        setattr(namespace, self.dest, resultObject)
        
    def getSecretFromOptions(self, options):
        secret = [s for s in options if s.startswith("secret=")]
        if len(secret) != 0:
            return secret[0][len("secret="):]
        else:
            secretFiles = [s for s in options if s.startswith("secretfile=")]
            if len(secretFiles) != 0:
                secretFile = secretFiles[0][len("secretfile="):]
                if not os.path.isfile(secretFile):
                    raise ArgumentTypeError('The given secret file "{0}" is no file.'.format(secretFile))
                with open(secretFile, "r") as f:
                    return f.read().strip()
            else:
                    raise ArgumentTypeError('You have to provide a secret or secret file.')
            
    def getValueForKey(self, options, key, required=True):
        entry = [s for s in options if s.startswith('{0}='.format(key))]
        if not required and entry is None:
            return None
        if required and entry is None:
            raise ArgumentTypeError('The option "{0}" is required.'.format(key))
        value = entry[0].split("=")[1]
        if len(value) is 0:
            raise ArgumentTypeError('The option "{0}" is required.'.format(key))
        return value
     
    @abstractmethod
    def getFileSaltIds(self):
        '''
        Returns the file salt ids.
        '''
        
    @abstractmethod
    def getFilenameSaltIds(self):
        '''
        Returns the file salt ids.
        '''
    

