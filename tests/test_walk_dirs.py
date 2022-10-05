import os
from test_commons import *

if __name__ == "__main__":
    for (root, dirs, files) in os.walk('.', topdown=True):
        print("The root is: ")
        print(root)
        print("The directories are: ")
        print(dirs)
        print("The files are: ")
        # print(files)
        for fileName in files:
            relativeFilePath = os.path.join(root, fileName)
            absoluteFilePath = os.path.abspath(relativeFilePath)
            print(absoluteFilePath)
        print('--------------------------------')