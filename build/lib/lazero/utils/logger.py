def sprint(*args, **kwargs):
    print(*args, **kwargs)
    print("_"*30)

def traceError(errorMsg:str="error!", _breakpoint:bool=False):
    import traceback
    traceback.print_exc()
    sprint(errorMsg)
    if _breakpoint:
        return breakpoint()