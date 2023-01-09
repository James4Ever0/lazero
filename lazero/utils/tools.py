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
from typing import Callable
def iteratorWrapper(iterator,init_repeat:int=0, repeat:int=0, max_iter:int=-1,before_yield:Callable=lambda:None, after_yield:Callable=lambda:None):
    # we use yield here.
    next_data = iterator.__next__()
    if init_repeat >0:
        for _ in range(init_repeat):
            yield next_data
    yield_counter = 0
    while True:
        if repeat <0:
            while True:
                yield next_data
        else:
            for _ in range(1+repeat):
                yield next_data
            try:
                next_data = iterator.__next__()
            except StopIteration:
                break
            yield_counter += 1
            if max_iter >=0:
                if yield_counter >= max_iter:
                    break