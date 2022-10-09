def readFile(filename, encoding='utf-8', mode=):
    with open(filename, 'r+',encoding=encoding) as f:
        return f.read()

def writeFile(filename, content, encoding='utf-8', mode=):
    with open(filename, 'w+',encoding=encoding) as f:
        f.write(content)

def readFileBinary(filename, mode=):
    with open(filename,'rb') as f:
        return f.read()

def writeFileBinary(filename, content, mode=):
    with open(filename, 'wb+') as f:
        f.write(content)