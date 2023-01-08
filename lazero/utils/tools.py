def flattenUnhashableList(list):
    return [x for x in flattenUnhashableListGenerator(list)]

def flattenUnhashableListGenerator(mList):
    for elem in mList:
        if type(elem) not in [list, tuple]:
            yield elem
        else:
            for elem2 in flattenUnhashableListGenerator(elem):
                yield elem2

def generatorUnwrap(generator, level=1):
    assert type(level) == int
    assert level >=0
    if level == 0:
        yield generator
    else:
        for x in generator:
            yield generatorUnwrap(x, level=level-1)

def iterator