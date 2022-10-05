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
):
    if os.path.exists(indexDirectory) and removeExists:
        shutil.rmtree(indexDirectory)
    print("whoosh indexing directory %s at %s" % (directory, indexDirectory))
    createIndexFromDataGenerator(
        enumerate(
            progressbar.progressbar(
                indexFilesInDirectory(
                    directory, removeExists=removeExists, withFileName=True
                )
            )
        ),
        indexDirectory,
    )
    print("whoosh index saved")
