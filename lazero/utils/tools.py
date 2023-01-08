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

def iteratorWrapper(iterator,init_repeat:int=0, repeat:int=0, max_iter:int=-1):
    # we use yield here.
    init_data = iterator.__next__()
    if init_repeat >0:
        for _ in range(init_repeat):
            