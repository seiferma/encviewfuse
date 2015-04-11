encviewfuse
===========
.. image:: https://secure.travis-ci.org/seiferma/encviewfuse.png
    :target: http://travis-ci.org/seiferma/encviewfuse

Description
-----------
encviewfuse is a fuse filesystem that provides an encrypted view on a given directory. You can use it in conjunction with usual backup software without the requirement to save the files encrypted or provide additional space.

Installation
------------
The file system is available for Python 3 via pypi (encviewfuse.fuse).

Usage
-----
``encviewfuse_fs <source directory> <mount point> -o secret=<secret>,fileSalt=<fileSalt>,filenameSalt=<filenameSalt>``

+-------------------------+-----------------------------------------------------------+
| Option Value            | Meaning                                                   |
+=========================+===========================================================+
| ``source directory``    | The directory containing the files to be encrypted        |
+-------------------------+-----------------------------------------------------------+
| ``mount point``         | The mount point for the encrypted view                    |
+-------------------------+-----------------------------------------------------------+
| ``secret``              | The secret used for the encryption                        |
+-------------------------+-----------------------------------------------------------+
| ``fileSalt``            | The id of the file salt provider (filename | mtime)       |
+-------------------------+-----------------------------------------------------------+
| ``filenameSalt``        | The id of the filename salt provider (filename | mtime)   |
+-------------------------+-----------------------------------------------------------+

Instead of the ``secret`` option, you can also use the ``secretfile`` option to specify a file containing the secret.