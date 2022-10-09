def readFile(filename, encoding='utf-8'):
    with open(filename, 'r+encoding=encoding) as f:
        return f.read()

def writeFile(filename, content, encoding='utf-8'):
    with open(filename, 'r+encoding=encoding) as f:
        f.write(content)

def readFileBinary(filename, encoding='utf-8'):
    with open(filename, encoding=encoding) as f:
        return f.read()

def writeFileBinary(filename, content, encoding='utf-8'):
    with open(filename, encoding=encoding) as f:
        f.write(content)