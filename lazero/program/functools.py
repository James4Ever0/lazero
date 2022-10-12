# print package name of this 'lazero.program.functools' package, please?
# print('PATH', __path__)
# print('NAME', __name__)
# # lazero.program.functools
# def someFunction():
#     print('NAME', __name__)
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


# import dill
from contextlib import suppress
import traceback


def skipException(
    debug_flag=False, breakpoint_flag=False, delayAfterException: int = 3, defaultReturn=None, global_variables:dict={}, local_variables:dict={}
):
    def wrapper(func):
        myExec = lambda command: exec(command, globals()|global_variables, locals()|local_variables) # new way of merging dicts in python 3.9, more 'functional'?
        def space_counter(line):
            counter = 0
            for x in line:
                if x == " ":
                    counter += 1
                else:
                    break
            return counter

        def remove_extra_return(code):
            while True:
                if "\n\n" in code:
                    code = code.replace("\n\n", "\n")
                else:
                    break
            return code

        def isEmptyLine(line):
            emptyChars = ["\n", "\t", "\r", " "]
            length = len(line)
            emptyCounts = 0
            for char in line:
                if char in emptyChars:
                    emptyCounts += 1
            return emptyCounts == length

        def getCodeBlocks(lines):
            mBlocks = []
            current_block = lines[0]
            lines = lines + [""]
            keywords = [" ", "def ", "async ", "with ", "class ", "@"]
            # keywords = [" ", "def", "async def", "with", "async with","class", "@"]
            for line in lines[1:]:
                if sum([line.startswith(keyword) for keyword in keywords]):
                    current_block += "\n"
                    current_block += line
                else:
                    mBlocks.append(current_block)
                    current_block = line
            return mBlocks

        def getExtendedLines(splited_code):
            splited_code = [x.rstrip() for x in splited_code]
            splited_code = "\n".join(splited_code).replace("\\\n", "")
            splited_code = remove_extra_return(splited_code)
            splited_code = splited_code.split("\n")
            return splited_code

        def reformatCode(func_code, MAXINT=10000000000, debug=False):
            # with open("test.py", "r") as f:
            code = func_code

            # need binary data.
            code_encoded = code.encode("utf-8")

            import subprocess

            command = (
                "autopep8 --max-line-length {MAXINT} - | black -l {MAXINT} -C -".format(
                    MAXINT=MAXINT
                )
            )
            commandLine = ["bash", "-c", command]
            result = subprocess.run(commandLine, input=code_encoded, capture_output=True)
            try:
                assert result.returncode == 0
                code_formatted = result.stdout.decode("utf-8")
            except:
                if debug:
                    import traceback

                    traceback.print_exc()
                    print("STDOUT", result.stdout)
                    print("STDERR", result.stderr)
                code_formatted = code
            if debug:
                print(code_formatted)
            return code_formatted

        def new_func(*args, **kwargs):
            func_name = func.__name__
            func_code = dill.source.getsource(func)
            # reformat the func code via our dearly autopep8-black formatter.
            func_code = reformatCode(func_code, debug=debug_flag)
            if debug_flag:
                print("########## FUNCTION CODE #########")
                print(
                    func_code
                )  # do not use chained decorator since doing so will definitely fail everything?
                print("########## FUNCTION CODE #########")
                print("########## FUNCTION #########")
            # print(func_code)
            func_code = remove_extra_return(func_code)
            splited_code = func_code.split("\n")
            splited_code = getExtendedLines(splited_code)
            # index 0: decorator
            # index 1: function name
            # no recursion support. may work inside another undecorated function.
            try:
                assert splited_code[0].strip().startswith("@skipException")
            except:
                raise Exception("Do not nesting the use of @skipException decorator")
            function_definition = splited_code[1]
            function_args = function_definition[:-1].replace("def {}".format(func_name), "")
            if debug_flag:
                print("FUNCTION ARGS:", function_args)
            kwdefaults = func.__defaults__
            pass_kwargs = {}

            if "=" in function_args:
                assert kwdefaults != None
                arg_remains = function_args.split("=")[0]
                kwarg_remains = function_args.replace(arg_remains, "")
                kwarg_extra_names = [
                    content.split(",")[-1].strip()
                    for index, content in enumerate(kwarg_remains.split("="))
                    if index % 2 == 1
                ]
                mfunctionArgsPrimitive = arg_remains.replace("(", "").split(",")
                kwarg_names = [mfunctionArgsPrimitive[-1].strip()] + kwarg_extra_names
                mfunctionArgs = mfunctionArgsPrimitive[:-1]
                if debug_flag:
                    print("PASSED KEYWORD ARGS:", kwargs)
                    print("KWARG NAMES:", kwarg_names)
                for key, value in zip(kwarg_names, kwdefaults):
                    pass_kwargs.update({key: value})
                for key in kwargs.keys():
                    assert key in kwarg_names
                    pass_kwargs[key] = kwargs[key]
            else:
                assert kwdefaults == None
                mfunctionArgs = function_args.replace("(", "").replace(")", "").split(",")
            mfunctionArgs = [x.strip() for x in mfunctionArgs]
            mfunctionArgs = [x for x in mfunctionArgs if not isEmptyLine(x)]
            if debug_flag:
                print("POSITIONAL ARGS:", mfunctionArgs)
            assert len(args) == len(mfunctionArgs)

            for key, value in zip(mfunctionArgs, args):
                myExec("{} = {}".format(key, value))
            if kwdefaults is not None:
                for key, value in pass_kwargs.items():
                    myExec("{} = {}".format(key, value))
            actualCode = splited_code[2:]
            actualCode = [x for x in actualCode if not isEmptyLine(x)]
            minIndent = min([space_counter(line) for line in actualCode])
            # split the code into different sections.
            if debug_flag:
                print(minIndent)
            newLines = [line[minIndent:] for line in actualCode]
            codeBlocks = getCodeBlocks(newLines)
            for block in codeBlocks:
                no_exception = False
                if debug_flag:
                    print("##########CODEBLOCK##########")
                    print(block)
                    print("##########CODEBLOCK##########")
                if not debug_flag:
                    with suppress(Exception):
                        myExec(block)
                        no_exception = True
                else:
                    try:
                        myExec(block)
                        no_exception = True
                    except:
                        traceback.print_exc()
                        if breakpoint_flag:
                            breakpoint()
                if not no_exception:
                    print("##########DELAY AFTER EXCEPTION##########")
                    import time

                    time.sleep(delayAfterException)
                    print("##########DELAY AFTER EXCEPTION##########")
            if debug_flag:
                print("########## FUNCTION #########")
            return defaultReturn
        return new_func
    return wrapper


def skipExceptionVerbose(func):
    return skipException(debug_flag=True)(func)


def skipExceptionBreakpoint(func):
    return skipException(breakpoint_flag=True)(func)


def skipExceptionDebug(func):
    return skipException(breakpoint_flag=True, debug_flag=True)(func)


# breakpoint()
from lazero.filesystem.temp import tmpdir
from typing import Union
from contextlib import nullcontext
from types import GeneratorType

# generators create generators. that's it.
def iterateWithTempDirectory(
    tempdir: Union[str, None] = None, targetType=GeneratorType
):
    # iterate is some added keyword.
    if tempdir is None:
        contextManager = lambda: nullcontext()
    else:
        contextManager = lambda: tmpdir(tempdir)

    def inner(func):
        def wrapper(  # default to be auto. otherwise why you use this?
            generatorMaybe, iterate: Literal[False, True, "auto"] = "auto", **kwargs
        ):  # this wrapper will void function input signatures maybe? anyway let's do it!
            if iterate == "auto":
                iterate = type(generatorMaybe) == targetType

            def iterator(generatorMaybe, **kwargs):
                for elem in generatorMaybe:
                    with contextManager():
                        yield func(elem, **kwargs)

            if iterate:
                return iterator(generatorMaybe, **kwargs)
            else:
                with contextManager():
                    return func(generatorMaybe, **kwargs)

        return wrapper

    return inner
