import progressbar
import shutil
import os
from lazero.search.api import lazeroCachePath
from lazero.search.index import indexFilesInDirectory
from lazero.search.txtai.model import embeddings


def txtaiIndexer(
    directory,
    indexDirectory=os.path.join(lazeroCachePath, "txtai_index"),
    removeExists=True,
    debug=False,
):
    iterator = indexFilesInDirectory(directory, removeExists=removeExists)
    if debug:
        iterator = progressbar.progressbar(iterator)
    if os.path.exists(indexDirectory) and removeExists:
        shutil.rmtree(indexDirectory)
    print("txtai indexing directory %s at %s" % (directory, indexDirectory))
    embeddings.index((uid, text, None) for uid, text in enumerate(iterator))
    embeddings.save(indexDirectory)
    print("txtai index saved")
