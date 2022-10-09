from test_commons import *
from lazero.network.asyncio import concurrentGet

# need json. what do you want?
url = "http://127.0.0.1:8932"
urlList = [url]*10

result = concurrentGet(urlList, processor = lambda x: dir(x))
print(result)
# object ClientResponse can't be used in 'await' expression
# so what?