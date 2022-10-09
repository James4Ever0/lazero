# this must be able to retrieve original file and linenumber based on index.

# but which database?

# get our 'home' directory first!
import os


def listFilesInDirectory(directory, debug=False):
    assert os.path.exists(directory)
    assert os.path.isabs(directory)
    # we assume this is plain directory with no further files?
    # we need absolute paths.
    filepaths = []
    for (root, dirs, files) in os.walk(directory, topdown=True):
        if debug:
            print("The root is: ")
            print(root)
            print("The directories are: ")
            print(dirs)
            print("The files are: ")
            # print(files)
        for fileName in files:
            relativeFilePath = os.path.join(root, fileName)
            absoluteFilePath = os.path.abspath(relativeFilePath)
            # yield absoluteFilePath
            filepaths.append(absoluteFilePath)
            if debug:
                print(absoluteFilePath)
        if debug:
            print("--------------------------------")
    filepaths.sort()  # make it deterministic.
    for filepath in filepaths:
        yield filepath


def getHomeDirectory():
    # https://pythonguides.com/get-current-directory-python/#:~:text=Get%20current%20directory%20Python%201%20To%20get%20the,can%20use%20another%20function%20called%20basename%20from%20os.path.
    return os.path.expanduser("~")  # well we borrow this from web.


lazeroCachePath = os.path.join(getHomeDirectory(), ".lazero")
if not os.path.exists(lazeroCachePath):
    os.mkdir(lazeroCachePath)
# what database you want to use? better test them first!
# really want anything related to database? what should you store?
# the index-to-file-with-linenumber mapping which txtai does not have.
# question: do you want to use graph database?
from unqlite import UnQLite
import progressbar

# binary?
# i plan to store and retrieve the value twice.
def storeKeyValuePairsToDatabase(
    data, databasePath=os.path.join(lazeroCachePath, "lazero_search.db"), debug=False
):
    db = UnQLite(databasePath)
    if debug:
        print("storing data to database: %s" % databasePath)
    with db.transaction():
        iterator = data
        if debug:
            iterator = progressbar.progressbar(iterator)
        for key, value in iterator:
            db[key] = value


def getValueByKeyFromDatabase(
    key, databasePath=os.path.join(lazeroCachePath, "lazero_search.db")
):
    db = UnQLite(databasePath)
    return db[key]

import json
def getLineStartEndInFileByConvLineIndexOriginalFromDatabase(line_index_original:int):
    start_end_json_string = getValueByKeyFromDatabase(str(line_index_original)).decode('utf-8')
    start_end_json = json.loads(start_end_json_string)
    start, end = start_end_json
    return start, end

from lazero.search.txtai.index import txtaiIndexer
from lazero.search.whoosh.index import whooshIndexer


def mainIndexer(
    directory,
    indexDirectories={
        "whoosh": os.path.join(lazeroCachePath, "whoosh_index"),
        "txtai": os.path.join(lazeroCachePath, "txtai_index"),
    },
):
    assert os.path.exists(directory)
    assert os.path.isdir(directory)
    assert os.path.isabs(directory)
    removeExists = True  # we don't want to create duplicates on the tinydb
    indexers = {"txtai": txtaiIndexer, "whoosh": whooshIndexer}
    for indexerName, indexDirectory in indexDirectories.items():
        indexer = indexers[indexerName]
        indexer(directory, indexDirectory=indexDirectory, removeExists=removeExists)
