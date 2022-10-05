
import threading

def startThread(target, args=(), kwargs={}):
    thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=False)
    thread.start()

def asyncThread(func):
    def new_func(*args, **kwargs):
        startThread(func, args=args, kwargs=kwargs)
    return new_func
