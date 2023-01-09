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
def iteratorWrapper(iterator,init_repeat:int=0, repeat:int=0, max_iter:int=-1,before_yield:Callable=lambda:None, after_yield:Callable=lambda:None, before_next:Callable=lambda:None, after_next:Callable=lambda:None):
    # we use yield here.
    before_next()
    next_data = iterator.__next__()
    after_next()
    if init_repeat >0:
        for _ in range(init_repeat):
            before_yield()
            yield next_data
            after_yield()
    yield_counter = 0
    while True:
        if repeat <0:
            while True:
                before_yield()
                yield next_data
                after_yield()
        else:
            for _ in range(1+repeat):
                before_yield()
                yield next_data
                after_yield()
            try:
                before_next()
                next_data = iterator.__next__()
                after_next()
            except StopIteration:
                break
            yield_counter += 1
            if max_iter >=0:
                if yield_counter >= max_iter:
                    break