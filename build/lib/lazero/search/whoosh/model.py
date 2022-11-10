from whoosh.fields import Schema, TEXT, STORED

from jieba.analyse import ChineseAnalyzer

analyzer = ChineseAnalyzer()
schema = Schema(
    # path=TEXT(stored=True, analyzer=analyzer), # maybe this is not needed, since you will have it anyway
    path_m1=TEXT(stored=True, analyzer=analyzer),
    path_m2=TEXT(stored=True, analyzer=analyzer),
    path_m3=TEXT(stored=True, analyzer=analyzer),
    path_m4=TEXT(stored=True, analyzer=analyzer),
    content=TEXT(stored=True, analyzer=analyzer),
    index=STORED(),
)

from whoosh.index import create_in

import os
from lazero.search.preprocessing import getFourVersionsOfProcessedLine


def createIndexFromDataGenerator(
    dataGenerator, indexDirectory, indexname="article_index"
):
    if not os.path.exists(indexDirectory):
        os.mkdir(indexDirectory)
    ix = create_in(indexDirectory, schema, indexname=indexname)
    writer = ix.writer()
    for (
        index,
        (content, filePath),
    ) in dataGenerator:  # as required you need to pass the data in given form.
        altered_paths = getFourVersionsOfProcessedLine(filePath)  # make it explicit.
        path_altered = {
            "path_m{}".format(index + 1): altered_paths[index] for index in range(4)
        }
        writer.add_document(content=content, index=index, **path_altered) # no path? really?
        # writer.add_document(path=filePath, content=content, index=index, **path_altered)
    writer.commit()
