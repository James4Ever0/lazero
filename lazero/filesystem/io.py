def readFile(filename, encoding='utf-8', mode='r+'):
    with open(filename, mode,encoding=encoding) as f:
        return f.read()

def writeFile(filename, content, encoding='utf-8', mode='w+'):
    with open(filename, mode,encoding=encoding) as f:
        f.write(content)

def readFileBinary(filename, mode=):
    with open(filename,'rb') as f:
        return f.read()

def writeFileBinary(filename, content, mode=):
    with open(filename, 'wb+') as f:
        f.write(content)