import os
from lazero.search.api import lazeroCachePath
from lazero.search.index import retrieveFilePathFromLineIndex


def updateDataDictWithLineIndexNormalizedScoreAndDivisor(
    dataDict,
    index,
    normalized_score,
    divisor,
    tinydbDatabasePath=os.path.join(lazeroCachePath, "index.json"),
):
    # this thing shall be stored in "the json based database".
    line_index_original, line_remainer = divmod(
        index, divisor
    )  # with or without original line?
    # content = getValueByKeyFromDatabase(str(line_index)+"_content")
    # it is just demonstration.
    filepath = retrieveFilePathFromLineIndex(index, databasePath=tinydbDatabasePath)

    filepathDataDict = dataDict.get(filepath, {})
    filepathLineIndexOriginalDataDict = filepathDataDict.get(line_index_original, {})
    filepathLineIndexOriginalDataDictLineRemainerScoreList = (
        filepathLineIndexOriginalDataDict.get(line_remainer, [])
    )  # shall you use the best score or the average score?

    filepathLineIndexOriginalDataDictLineRemainerScoreList.append(normalized_score)

    filepathLineIndexOriginalDataDict.update(
        {line_remainer: filepathLineIndexOriginalDataDictLineRemainerScoreList}
    )
    filepathDataDict.update({line_index_original: filepathLineIndexOriginalDataDict})
    dataDict.update({filepath: filepathDataDict})
    return dataDict


# so you have both search methods in whoosh and txtai.
# first get the config, the 'withOriginalLine' from tinydb
from lazero.search.txtai.search import txtaiSearch
from lazero.search.whoosh.search import whooshSearch
from lazero.search.index import retrieveConfig

# import statistics


def weightedMean(data, epsilon=1e-3):
    weightTotal = sum(data) + epsilon
    mean = sum([value**2 for value in data]) / weightTotal
    return mean


def search(
    query,
    indexDirectories={
        "txtai": os.path.join(lazeroCachePath, "txtai_index"),
        "whoosh": os.path.join(lazeroCachePath, "whoosh_index"),
    },
    limit=100,
    tinydbDatabasePath=os.path.join(lazeroCachePath, "index.json"),
    filter_filepath=None,
    methods={
        "subLineScore": weightedMean,  # statistics.mean
        "lineScore": max,
        "fileScore": max,
    },
):  # so we use 'indexDirectories' alone to determine the backends.
    assert indexDirectories != {}  # not using empty index here.
    dataDict = {}
    withOriginalLine = retrieveConfig("withOriginalLine")  # retrieve this from tinydb.
    if "txtai" in indexDirectories.keys():
        dataDict = txtaiSearch(
            query,
            indexDirectories["txtai"],
            filter_filepath=filter_filepath,
            limit=limit,
            withOriginalLine=withOriginalLine,
            tinydbDatabasePath=tinydbDatabasePath,
            dataDict=dataDict,
        )
    if "whoosh" in indexDirectories.keys():
        dataDict = whooshSearch(  # so we hide some parameters for whoosh.
            query,
            indexDirectories["whoosh"],
            filter_filepath=filter_filepath,
            limit=limit,
            withOriginalLine=withOriginalLine,
            tinydbDatabasePath=tinydbDatabasePath,
            dataDict=dataDict,
        )
    # the hard part. we need to retrieve 粗排 精排 data here.
    # what is the structure of the dataDict?
    # {} -> filepath -> {} -> line_index_original -> {} -> line_remainder -> [] (the score of this single line.)

    # you also need to merge lines if you have to.
    # for every file, show no more than three related lines.
    # but you need to ensure that you can jump to them, just in case.
    # no need to merge lines if they overlap.
    fileRankList = []
    lineRankListInFileAsDict = {}
    lineRankListInAllFiles = []
    for filepath, linesDict in dataDict.items():
        lineScores = []
        for line_index_original, subLinesDict in linesDict.items():
            subLineScores = []
            for line_remainer, scoreList in subLinesDict.items():
                subLineScore = methods["subLineScore"](scoreList)
                subLineScores.append(subLineScore)
            lineScore = methods["lineScore"](subLineScores)
            lineScores.append(lineScore)
            lineScoreWithOriginalIndex = {
                "line_index_original": line_index_original,
                "score": lineScore,
            }
            lineScreWithOriginalIndexAndFilePath = {"filepath": filepath}
            lineScreWithOriginalIndexAndFilePath.update(lineScoreWithOriginalIndex)
            lineRankListInFileAsDict.update(
                {
                    filepath: lineRankListInFileAsDict.get(filepath, [])
                    + [lineScoreWithOriginalIndex]
                }
            )
            lineRankListInAllFiles.append(lineScreWithOriginalIndexAndFilePath)
        # 精排
        lineRankListInFileAsDict[filepath].sort(key=lambda x: -x["score"])
        fileScore = methods["fileScore"](lineScores)
        fileRankList.append({"filepath": filepath, "score": fileScore})
    # 粗排
    fileRankList.sort(key=lambda x: -x["score"])
    lineRankListInAllFiles.sort(key=lambda x: -x["score"])
    return (
        fileRankList,
        lineRankListInFileAsDict,
        lineRankListInAllFiles,  # maybe you need this shit?
    )
    # ready to render this shit?
    # you want to display score or not?
    # as the title on panel?
