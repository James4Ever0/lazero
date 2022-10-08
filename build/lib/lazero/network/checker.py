
def waitForServerUp(port, message, timeout=1):
    import requests
    while True:
        try:
            url = "http://localhost:{}".format(port)
            with requests.get(url, timeout=timeout, proxies=None) as r:
                if type(message) == str:
                    text = r.text.strip('"').strip("'")
                else:
                    text = r.json()
                print("SERVER AT PORT %d RESPONDS:" % port, [text])
                assert text == message
                print("SERVER AT PORT %d IS UP" % port)
                break
        except:
            import traceback

            traceback.print_exc()
            print("SERVER AT PORT %d MIGHT NOT BE UP" % port)
            print("EXPECTED MESSAGE:", [message])
            import time

            time.sleep(1)
