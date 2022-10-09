def readFile(filename, encoding="utf-8", mode="r+"):
    with open(filename, mode, encoding=encoding) as f:
        return f.read()


def writeFile(filename, content, encoding="utf-8", mode="w+"):
    with open(filename, mode, encoding=encoding) as f:
        f.write(content)


def readFileBinary(filename, mode="rb"):
    with open(filename, mode) as f:
        return f.read()


def writeFileBinary(filename, content, mode="wb+"):
    with open(filename, mode) as f:
        f.write(content)

import pickle
import dill
from typing import Literal
backends = {'pickle': pickle, 'dill': dill}
def readPythonObjectFromFile(filename, backend:Literal['pickle', 'dill']=''):
    data = readFileBinary(filename)
    return pickle.loads(data)