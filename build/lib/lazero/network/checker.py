def waitForServerUp(port, message, timeout=1, maxtime=-1,host='localhost'):
    import requests

    mtime = maxtime if (mflag := maxtime > 0) else 1
    while mtime > 0:
        try:
            if mflag:
                mtime -= 1
                print(f"{mtime} chances remains for server {port} at {host}")
            url = "http://{}:{}".format(host,port)
            with requests.get(url, timeout=timeout, proxies=None) as r:
                if type(message) == str:
                    text = r.text.strip('"').strip("'")
                else:
                    text = r.json()
                print("SERVER AT PORT %d RESPONDS:" % port, [text])
                assert text == message
                print("SERVER AT PORT %d IS UP" % port)
                # break
                return True
            # better just return
        except:
            import traceback

            traceback.print_exc()
            print("SERVER AT PORT %d MIGHT NOT BE UP" % port)
            print("EXPECTED MESSAGE:", [message])
            import time

            time.sleep(1)
    return False