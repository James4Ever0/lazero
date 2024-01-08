from test_commons import *
from lazero.search.api import getValueByKeyFromDatabase, storeKeyValuePairsToDatabase

keyValuePairs = [("test", "value")]
try:
    # after first test, check if data persists.
    result = getValueByKeyFromDatabase("test")
    print("RESULT:", result)  # binary. need to decode.
except:
    import traceback

    traceback.print_exc()
for _ in range(2):
    storeKeyValuePairsToDatabase(keyValuePairs)
    result = getValueByKeyFromDatabase("test")
    print("RESULT:", result)  # binary. need to decode.
    # there is only one such result. unique.
    # still we only have one such result.
