import os
from lazero.search.api import (
    lazeroCachePath,
    listFilesInDirectory,
    storeKeyValuePairsToDatabase,
)
from lazero.search.preprocessing import (
    getLineWiseAndListOfCleanedMergedConvGroupWithLineIndexMappingFromStringReadFromFile,
    getFourVersionOfLineInListOfCleanedMergedConvGroupWithLineIndexMapping,
)
import tinydb
import json

from tinydb import Query

from functools import lru_cache


@lru_cache(maxsize=1)
def tinydbQueryBootstrap(databasePath=os.path.join(lazeroCachePath, "index.json")):
    User = Query()
    if not os.path.exists(databasePath):
        raise Exception("Could not find tinydb database path:", databasePath)
    database = tinydb.TinyDB(databasePath)
    return User, database


def retrieveFilePathFromLineIndex(
    line_index, databasePath=os.path.join(lazeroCachePath, "index.json")
):
    # line index need not to be normalized.
    User, database = tinydbQueryBootstrap(databasePath)

    results = database.search((User.start <= line_index) & (User.end >= line_index))
    path = results[0]["path"]
    return path


def retrieveLineRangeFromFilePath(
    filepath, databasePath=os.path.join(lazeroCachePath, "index.json")
):
    # line index need not to be normalized.
    User, database = tinydbQueryBootstrap(databasePath)

    results = database.search((User.path == filepath))
    data = results[0]
    start, end = data["start"], data["end"]
    return start, end  # inclusive.


def retrieveConfig(name, databasePath=os.path.join(lazeroCachePath, "index.json")):
    User, database = tinydbQueryBootstrap(databasePath)
    results = database.search((User.name == name))
    data = results[0]
    value = data["value"]
    return value


import progressbar


def checkEndsWithinAllowedExtensions(filepath, allowedExtensions: list):
    for ext in allowedExtensions:
        if filepath.endswith(ext):
            return True
    return False


def indexFilesInDirectory(
    directory,
    databasePath=os.path.join(lazeroCachePath, "index.json"),
    removeExists=True,
    withFileName=False,
    withOriginalLine=True,
    allowedExtensions=[".md", ".txt", ".html"],
):
    # we make this process atomic. if the path exists then we will remove it.
    if os.path.exists(databasePath) and removeExists:
        os.remove(databasePath)
    database = tinydb.TinyDB(databasePath)
    database.insert({"name": "withOriginalLine", "value": withOriginalLine})
    counter = 0
    divisor = 4 + int(withOriginalLine)
    # you need to ignore .git directory.
    for absoluteFilePath in progressbar.progressbar(
        [
            x
            for x in listFilesInDirectory(directory)
            if "/.git/" not in x
            and checkEndsWithinAllowedExtensions(x, allowedExtensions)
        ]
    ):
        temp_processed_line_index_mapping = []
        try:
            with open(absoluteFilePath, "r", encoding="utf8") as f:
                data = f.read()
        except:
            # there's PNG in the path.
            continue
        (
            linewise,
            listOfCleanedMergedConvGroupWithLineIndexMapping,
        ) = getLineWiseAndListOfCleanedMergedConvGroupWithLineIndexMappingFromStringReadFromFile(
            data
        )

        total_length = (
            len(listOfCleanedMergedConvGroupWithLineIndexMapping) * divisor
        )  # because we use the original line.
        # total_length = len(linewise) * divisor # because we use the original line.
        # total_length = len(linewise) * divisor # because we use the original line.
        # index >= start and index <= end
        start = counter
        end = counter + total_length - 1
        counter += total_length
        database.insert({"path": absoluteFilePath, "start": start, "end": end})
        # shall we change the end index into something inclusive? you need to minus one.
        # print(len(listOfCleanedMergedConvGroupWithLineIndexMapping))
        # 1421 vs 13235: 9.31
        # print('total_length:',total_length)
        # breakpoint()
        for index in range(total_length):
            if index % divisor != 0:
                continue
            line_range = listOfCleanedMergedConvGroupWithLineIndexMapping[
                index // divisor
            ]["line_range"]
            mIndex = start + index
            temp_processed_line_index_mapping.append(
                (str(mIndex // divisor), json.dumps(line_range))
            )
            # mIndex2 = start/divisor + index
            temp_processed_line_index_mapping.append(  # here's how we store the original conv_group content
                (
                    str(mIndex // divisor) + "_content",
                    listOfCleanedMergedConvGroupWithLineIndexMapping[index // divisor][
                        "conv_group_merged"
                    ],
                )
            )
        temp_processed_line_index_mapping = list(set(temp_processed_line_index_mapping))
        storeKeyValuePairsToDatabase(temp_processed_line_index_mapping)

        for (
            changed_lines
        ) in getFourVersionOfLineInListOfCleanedMergedConvGroupWithLineIndexMapping(
            listOfCleanedMergedConvGroupWithLineIndexMapping,
            withOriginalLine=withOriginalLine,
        ):
            # you may yield them one by one.
            for changed_line in changed_lines:
                if withFileName:
                    yield changed_line, absoluteFilePath
                else:
                    yield changed_line
