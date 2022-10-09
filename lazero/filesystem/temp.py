from contextlib import AbstractContextManager
from ctypes import Union
import os
import shutil
import uuid


class tmpdir(AbstractContextManager):
    """Context manager to suppress specified exceptions

    After the exception is suppressed, execution proceeds with the next
    statement following the with statement.

         with suppress(FileNotFoundError):
             os.remove(somefile)
         # Execution still resumes here if the file was already removed
    """

    def __init__(self, path=None):
        assert type(path) == str
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        self._tmpdir = path

    def __str__(self):
        return os.path.abspath(self._tmpdir)

    def __repr__(self):
        return os.path.abspath(self._tmpdir)

    def __enter__(self):
        print("temporary directory: %s" % self._tmpdir)
        if os.path.exists(self._tmpdir):
            shutil.rmtree(self._tmpdir)
        os.makedirs(self._tmpdir)
        return self._tmpdir

    def __exit__(self, exctype, excinst, exctb):
        # try not to handle exceptions?
        tempdir = self._tmpdir
        print("cleaning tempdir: %s" % tempdir)
        if os.path.exists(tempdir):
            if os.path.isdir(tempdir):
                shutil.rmtree(tempdir)
        return False


class tmpfile(AbstractContextManager):
    def __init__(self, path=None, replace=False):
        assert type(path) == str
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if os.path.exists(path):
            if replace:
                import shutil

                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            else:
                raise Exception("file %s already exists" % path)
        self._tmpdir = os.path.dirname(path)
        self._filepath = path

    def __enter__(self):
        print("allocating temporary directory: %s" % self._tmpdir)
        if not os.path.exists(self._tmpdir):
            os.makedirs(self._tmpdir)
        return self._filepath

    def __exit__(self, exctype, excinst, exctb):
        # try not to handle exceptions?
        tempdir = self._tmpdir
        tempfile = self._filepath
        print("cleaning tempfile: %s" % tempdir)
        if os.path.exists(tempfile):
            if os.path.isfile(tempfile):
                os.remove(tempfile)
            elif os.path.isdir(tempfile):
                shutil.rmtree(tempfile)
        if os.path.exists(tempdir):
            if os.path.isdir(tempdir):
                if os.listdir(tempdir) == []:
                    print("removing empty tempdir: %s" % tempdir)
                    shutil.rmtree(tempdir)
        return False


def getRandomFileNameUnderDirectoryWithExtension(extension: str, directory: str):
    assert os.path.exists(directory)
    assert os.path.isdir(directory)
    while True:
        filepath = os.path.join(directory, ".".join([str(uuid.uuid4()), extension]))
        if not os.path.exists(filepath):
            return filepath

def iterateWithTempDirectory(tempdir:Union[str, None]=None):
    # iterate is some added keyword.
    def inner(func):
        def wrapper(*args,iterate=False,**kwargs): # this wrapper will void function input signatures maybe? anyway let's do it!
            if iterate:
            return func
    
    return inner