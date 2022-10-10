import progressbar
import shutil
import os
from lazero.search.api import lazeroCachePath
from lazero.search.index import indexFilesInDirectory
from lazero.search.whoosh.model import createIndexFromDataGenerator


def whooshIndexer(
    directory,
    indexDirectory=os.path.join(lazeroCachePath, "whoosh_index"),
    removeExists=True,
    debug=False,
):
    iterator = indexFilesInDirectory(
        directory, removeExists=removeExists, withFileName=True
    )
    if debug:
        iterator = progressbar.progressbar(iterator)
    if os.path.exists(indexDirectory) and removeExists:
        shutil.rmtree(indexDirectory)
    print("whoosh indexing directory %s at %s" % (directory, indexDirectory))
    createIndexFromDataGenerator(
        enumerate(iterator),
        indexDirectory,
    )
    print("whoosh index saved")
