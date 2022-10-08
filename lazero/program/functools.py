# print package name of this 'lazero.program.functools' package, please?
# print('PATH', __path__)
# print('NAME', __name__)
# # lazero.program.functools
# def someFunction():
#     print('NAME',__name__)
# lazero.program.functools
# it is the same!
# what about let's call it elsewhere?
## reserved keyword: __pickled_arguments__
from typing import Literal, Union
import argparse
import os
import pickle
import dill
from contextlib import AbstractContextManager
import subprocess
from lazero.filesystem.temp import tmpfile
import uuid


class workingDirectoryManager(AbstractContextManager):
    def __init__(
        self,
        workingDirectory: Union[str, None],
    ):
        self.currentWorkingDirectory = os.path.abspath(os.curdir)
        self.workingDirectory = workingDirectory

    def __enter__(self):
        if self.workingDirectory:
            assert os.path.isabs(self.workingDirectory)
            os.chdir(self.workingDirectory)

    def __exit__(self, exctype, excinst, exctb):
        if self.workingDirectory:
            os.chdir(self.currentWorkingDirectory)


def pickledFunction(
    packageName,
    workingDirectory: Union[None, str] = None,
    debug=False,
    backend: Literal["dill", "pickle"] = "dill",
):
    # this decorator is used inside a specific INSTALLED package like pyjom. if you want to use it for non-installed package, better set the working directory for this decorator.
    backendMap = {"dill": dill, "pickle": pickle}
    currentBackend = backendMap[backend]
    if debug:
        print("package name: %s" % packageName)

    def inner(func):
        funcName = func.__name__
        argumentFlag = "--{}".format(funcName)
        if debug:
            print("function name: %s" % funcName)
        if (
            packageName == "__main__"
        ):  # this will accept nothing as argument or keyword arguments
            parser = argparse.ArgumentParser()
            parser.add_argument(argumentFlag, type=str, default="")
            parsed_args = parser.parse_args()
            picklePath = parsed_args.__dict__[funcName]
            if picklePath == "":
                ...
            elif os.path.exists(picklePath):
                with open(picklePath, "rb") as f:
                    pickledArguments = currentBackend.load(f)
                args = pickledArguments["args"]
                kwargs = pickledArguments["kwargs"]
                if debug:
                    print("function args: %s" % args)
                    print("function kwargs: %s" % kwargs)
                result = func(*args, **kwargs)
                with open(picklePath, "wb") as f:
                    currentBackend.dump(result, f)
                if debug:
                    print("function result: %s" % result)
            else:
                raise Exception("nonexistant pickle path:", picklePath.__repr__())
        else:
            # if workingDirectory:
            def wrapper(*args, **kwargs):
                pickledArguments = {}
                pickledArguments["args"] = args
                pickledArguments["kwargs"] = kwargs
                # you need to get current working directory first.
                # also you need a context manager to deal with problems, being able to get back to current working directory no matter what.
                pickleFileName = "{}.{}".format(
                    str(uuid.uuid4()).replace("-", "_"), backend
                )
                pickleFilePath = os.path.join(
                    "/dev/shm/pickledFunctionParameters", pickleFileName
                )
                with tmpfile(pickleFilePath):
                    with open(pickleFilePath, "wb") as f:
                        currentBackend.dump(pickledArguments, f)
                        if debug:
                            print("arguments dumped to %s" % pickleFilePath)
                    with workingDirectoryManager(
                        workingDirectory
                    ):  # this parameter could be None.
                        commandArguments = [
                            "python3",
                            "-m",
                            packageName,
                            argumentFlag,
                            pickleFilePath,
                        ]
                        result = subprocess.run(
                            commandArguments,
                            shell=False,
                        )
                        assert result.returncode == 0
                        if debug:
                            print("subprocess execution done")
                    with open(pickleFilePath, "rb") as f:
                        return currentBackend.load(f)

            return wrapper
        return lambda: None  # a symbolic function.

    return inner
