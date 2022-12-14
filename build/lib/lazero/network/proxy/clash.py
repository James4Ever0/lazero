# from faulthandler import disable
from xmlrpc.client import MAXINT
from lazero.network.asyncio import concurrentGet
import os
import json
from typing import Literal, Union

# from pprint import pprint

os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
localhost = "http://127.0.0.1"
localhostWithPort = lambda port: "{}:{}".format(localhost, port)
import requests

# so, how do you get the proxy list and test the speed for deepl.com?
# if you really want to fall back, just change the proxy config.
def getProxyList(
    port: int = 9911,
    debug=False,
    disallowed_types=["URLTest", "Reject", "Selector", "Direct", "Fallback"],
):  # default do not return proxy groups. only standalone proxies.
    clashUrl = localhostWithPort(port) + "/proxies"  # this will reduce one layer of "/"
    if debug:
        print(clashUrl)
    r = requests.get(clashUrl)
    # return r.content
    proxyInfo = r.json()
    # pprint(proxyInfo)
    proxyList = []
    for proxyName, proxy in proxyInfo["proxies"].items():
        proxyType = proxy["type"]
        # print(proxyType)
        if proxyType not in disallowed_types:
            proxyList.append(proxyName)
    # proxyList = [key for key in proxyInfo["proxies"].keys()]
    return proxyList


def testProxyList(
    proxyList,
    port: int = 9911,
    url="https://deepl.com",
    # debug=False,
    timeout: int = 3000,  # in miliseconds?
    valid=True,  # only return those with valid delay values.
):  # test the speed for given url
    # first, generate the proper list of requests.
    params = {"timeout": timeout, "url": url}
    url_list = [
        localhostWithPort(port) + "/proxies/{}/delay".format(proxyName)
        for proxyName in proxyList
    ]
    delayList = concurrentGet(url_list, processor=lambda x: x.json(), params=params)
    validProxyDelayList = []
    proxyDelayList = zip(delayList, proxyList)
    for delayDict, proxyName in proxyDelayList:
        info = {"name": proxyName}
        if "delay" in delayDict.keys():  # we only get those with valid responses.
            # delay = delayDict["delay"]
            info.update(delayDict)
            validProxyDelayList.append(info)
        elif valid == False:
            info.update({"delay": MAXINT})  # remove these first, please?
            validProxyDelayList.append(info)
    validProxyDelayList.sort(key=lambda x: x["delay"])
    return validProxyDelayList


def setProxyWithSelector(
    proxyName, selector="GLOBAL", port: int = 9911, debug=False
):  # how to make sure it will use 'GLOBAL'? it needs to be done with the config.
    if debug:
        print("select proxy %s with selector %s" % (proxyName, selector))
    clashUrl = localhostWithPort(port) + "/proxies/{}".format(selector)
    r = requests.put(
        clashUrl, data=json.dumps({"name": proxyName}, ensure_ascii=False).encode()
    )
    try:
        assert r.status_code == 204
    except:
        import traceback

        traceback.print_exc()
        try:
            print(r.content)
            print("error code:", r.status_code)
        except:
            ...
        print("error when setting proxy %s with selector %s" % (proxyName, selector))


def setProxyConfig(
    port: int = 9911,
    http_port: Union[None, int] = None,
    mode: Literal[
        "Global", "Rule", "Direct", None
    ] = None,  # currently this mode is configured as 'rule' so everything related to 'deepl' will be redirected.
):
    # https://clash.gitbook.io/doc/restful-api/config
    # sure you can patch more things but that's enough for now.
    clashUrl = localhostWithPort(port) + "/configs"
    configs = {}
    if http_port:
        configs.update({"port": http_port})
    if mode:
        configs.update({"mode": mode})
    r = requests.patch(clashUrl, data=json.dumps(configs, ensure_ascii=False).encode())
    assert r.status_code == 204


def getConnectionGateway(
    port: int = 9911,
):  # get the clash local http proxy connection port.
    clashUrl = localhostWithPort(port) + "/configs"
    r = requests.get(clashUrl)
    configs = r.json()
    http_port = configs["port"]
    gateway = localhostWithPort(http_port)
    return gateway


def getTestedProxyList(
    port: int = 9911,
    debug=False,
    disallowed_types=["URLTest", "Reject", "Selector", "Direct", "Fallback"],
    url="https://deepl.com",
    timeout: int = 5000,  # in miliseconds?
    valid=True,
):
    proxyList = getProxyList(debug=debug, port=port, disallowed_types=disallowed_types)
    # pprint.pprint(result)
    validProxyDelayList = testProxyList(
        proxyList, timeout=timeout, url=url, valid=valid
    )
    return validProxyDelayList


from contextlib import AbstractContextManager


class clashProxyStateManager(AbstractContextManager):
    def __init__(
        self,
        enter: Literal["Global", "Rule", "Direct", None],
        exit: Literal["Global", "Rule", "Direct", None],
        port=9911,
    ):
        self.enter = enter
        self.exit = exit
        self.port = port

    def __enter__(self):
        setProxyConfig(port=self.port, mode=self.enter)

    def __exit__(self, exctype, excinst, exctb):
        setProxyConfig(port=self.port, mode=self.exit)
        return
