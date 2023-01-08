from lazero.search.txtai.model import embeddings
from functools import lru_cache
import os

from ..index import retrieveLineRangeFromFilePath
from ...utils.mathlib import checkMinMaxDict


@lru_cache(maxsize=1)
def txtaiSearchBootstrap(indexDirectory):
    assert os.path.exists(indexDirectory)
    assert os.path.isabs(indexDirectory)
    embeddings.load(indexDirectory)
    print("Loaded txtaiSearchBootstrap index directory: " + indexDirectory)


def txtaiSearchSingle(
    search_query_processed,
    indexDirectory,
    limit=100,
    filter_filepath=None,  # to search for specific file only.
    # does this freaking filter work?
):  # why don't you have filter path related to the specific file damn?
    # maybe you can do it later on. fuck.
    txtaiSearchBootstrap(indexDirectory)
    uid_list_tops = embeddings.search(search_query_processed, limit)
    if filter_filepath:
        start, end = retrieveLineRangeFromFilePath(filter_filepath)
        lineRangeFilter = {"min": start, "max": end}

    for index, score in uid_list_tops:
        # uid = int(uid)
        # where is the damn score? wtf?
        if filter_filepath:
            result = checkMinMaxDict(index, lineRangeFilter)
            if not result:
                continue  # do not use results other than the selected file.
        # answer = data_source[uid]
        # the uid is the raw index.
        # print("{}:".format(uid), answer)
        # print("score:", score)
        yield index, score


import os
from lazero.search.api import lazeroCachePath
from lazero.search.search import updateDataDictWithLineIndexNormalizedScoreAndDivisor
from lazero.search.preprocessing import getFourVersionsOfProcessedLine


def txtaiSearch(
    query,
    indexDirectory,
    filter_filepath=None,
    limit=100,
    withOriginalLine=True,  # this is default behavior of indexer. you still need to retrieve this flag from tinydb.
    tinydbDatabasePath=os.path.join(lazeroCachePath, "index.json"),
    dataDict={},
):

    divisor = 4 + int(withOriginalLine)

    fourProcessedLines = list(getFourVersionsOfProcessedLine(query))
    for search_query_processed in (
        [query] if withOriginalLine else []
    ) + fourProcessedLines:
        for index, normalized_score in txtaiSearchSingle(
            search_query_processed,
            indexDirectory,
            limit=limit,
            filter_filepath=filter_filepath,
        ):
            dataDict = updateDataDictWithLineIndexNormalizedScoreAndDivisor(
                dataDict,
                index,
                normalized_score,
                divisor,
                tinydbDatabasePath=tinydbDatabasePath,
            )
    return dataDict
