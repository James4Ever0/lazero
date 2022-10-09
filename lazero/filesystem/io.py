def readFile(filename, encoding='utf-8'):
    with open(filename, encoding=encoding) as f:
        return f.read(encoding)