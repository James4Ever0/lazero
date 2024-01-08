from test_commons import *
from lazero.search.api import getValueByKeyFromDatabase
from lazero.utils.logger import sprint
for index in range(100):
    value = getValueByKeyFromDatabase(str(index)+"_content").decode("utf8")
    print("INDEX:", index)
    sprint('VALUE:', value)