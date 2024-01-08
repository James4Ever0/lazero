# from lazero.search.whoosh.model import analyzer
# we do highligh in another way.
from whoosh.index import open_dir
from whoosh import qparser
from whoosh.query import Term
from lazero.search.preprocessing import getFourVersionsOfProcessedLine
from functools import lru_cache


@lru_cache(maxsize=1)
def whooshSearchBootstrap(
    indexDirectory,
    search_fields:tuple=("path_m1", "path_m2", "path_m3", "path_m4", "content"),
    indexname="article_index",
):
    search_fields = list(search_fields)
    assert os.path.exists(indexDirectory)
    assert os.path.isabs(indexDirectory)
    ix = open_dir(indexDirectory, indexname=indexname)
    schema = ix.schema

    og = qparser.OrGroup.factory(0.9)
    mp = qparser.MultifieldParser(search_fields, schema, group=og)
    print("Loaded whooshSearchBootstrap index directory: " + indexDirectory)
    return ix, schema, og, mp


def whooshSearchSingle(
    search_query_processed,
    indexDirectory,
    search_fields:tuple=("path_m1", "path_m2", "path_m3", "path_m4", "content"),
    indexname="article_index",
    epsilon=1e-3,
    limit=100,
    weight=0.7,
    filter_filepath=None,  # to search for specific file only.
):  # remember that 'path' is not 'multiplexed'
    # ix, schema, og, mp = whooshSearchBootstrap(indexDirectory, search_fields=search_fields,indexname=indexname)
    # maybe they don't need some.
    ix, _, _, mp = whooshSearchBootstrap(
        indexDirectory, search_fields=search_fields, indexname=indexname
    )

    q = mp.parse(search_query_processed)
    with ix.searcher() as s:
        if filter_filepath:
            allow_q = Term("path", filter_filepath)
            results = s.search(q, terms=True, limit=limit, filter=allow_q)
        else:
            results = s.search(q, terms=True, limit=limit)  # what fucking terms?
        # we don't need this stuff no more.
        # cause your index is bloated.
        # results.fragmenter.charlimit = 100000
        lastScore = 2
        maxScore = 0
        for hitIndex, hit in enumerate(results):
            # content = hit["content"] # the content is not important. we need original content, not these fake shits.
            score = hit.score
            if score < epsilon:
                score = lastScore / 2
            if hitIndex == 0:
                maxScore = score
            lastScore = score
            normalized_score = (score / maxScore) * weight
            index = hit["index"]
            yield index, normalized_score
            # path = hit['path']
            # we need some unified interface to process this shit.


# from lazero.search.whoosh.api import getValueByKeyFromDatabase
import os
from lazero.search.api import lazeroCachePath
from lazero.search.search import updateDataDictWithLineIndexNormalizedScoreAndDivisor


def whooshSearch(
    query,
    indexDirectory,
    search_fields:tuple=("path_m1", "path_m2", "path_m3", "path_m4", "content"),
    indexname="article_index",
    epsilon=1e-3,
    limit=100,
    filter_filepath=None,
    weight=0.7,  # do not mark our top hit as '100% certain'
    withOriginalLine=True,  # this is default behavior of indexer. you still need to retrieve this flag from tinydb.
    tinydbDatabasePath=os.path.join(lazeroCachePath, "index.json"),
    dataDict={},  # for using with txtai
):  # will multiplex the thing.
    divisor = 4 + int(withOriginalLine)

    fourProcessedLines = list(getFourVersionsOfProcessedLine(query))
    for search_query_processed in (
        [query] if withOriginalLine else []
    ) + fourProcessedLines:
        for index, normalized_score in whooshSearchSingle(
            search_query_processed,
            indexDirectory,
            search_fields=search_fields,
            indexname=indexname,
            limit=limit,
            weight=weight,
            epsilon=epsilon,
            filter_filepath=filter_filepath,
        ):
            dataDict = updateDataDictWithLineIndexNormalizedScoreAndDivisor(
                dataDict,
                index,
                normalized_score,
                divisor,
                tinydbDatabasePath=tinydbDatabasePath,
            )
    # you decide what to do with dataDict later.
    return dataDict
