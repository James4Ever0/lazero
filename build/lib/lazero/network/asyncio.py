import aiohttp
import asyncio
# from contextlib import closing

# clearly it is not clean enough.
# also i worry about the memory leakage, open file limit exceeding.
async def get(url, processor=lambda x: x, params={}):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            result = await processor(response)
            return result

from lazero.program.functools import pickledFunction
# let's test this first?
@pickledFunction(__name__, debug=False) # use pickle to store args/kwargs, return values, within the same directory.
def concurrentGet(
    url_list, processor=lambda x: x, params={}, debug=False,
    # child_process=True
):
    # with closing(asyncio.get_event_loop()) as loop:  # this closing is not working properly.
    loop = asyncio.get_event_loop() # this event loop is already running! fuck. we must use some 'magic' method here...
    multiple_requests = [
        get(url, processor=processor, params=params) for url in url_list
    ]
    results = loop.run_until_complete(asyncio.gather(*multiple_requests))
    if debug:
        print("Results: %s" % results)
    return results

if __name__ == '__main__':
    concurrentGet()