import requests

class netProgressbar:
    def __init__(self, port = 8576, timeout=1,message = 'progressbar server'):
        from lazero.network import waitForServerUp
        self.port = port
        self.message = message
        self.timeout=timeout
        waitForServerUp(port=port, message=message)
    def reset(self, total:int):
        try:
            with requests.get('http://localhost:{}/reset'.format(self.port),proxies=None,params = {'total':total}, timeout=self.timeout) as conn:
                print("connection status:", conn)
        except:
            import traceback
            traceback.print_exc()
            print("error when resetting netProgressbar")
    def update(self,progress:int=1, info=""):
        info = str(info)
        try:
            with requests.get('http://localhost:8576/update',proxies=None, params={'progress':progress,'info':info}, timeout=self.timeout) as conn:
                print("connection status:", conn)
        except:
            import traceback
            traceback.print_exc()
            print("error when updating netProgressbar")