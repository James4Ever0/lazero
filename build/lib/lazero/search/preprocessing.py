def removeDuplicates(line, chars=[" ", "\t"], maxConsecutiveLength=1):
    for char in chars:
        minUnallowedConsecutiveLength = maxConsecutiveLength + 1
        while True:
            if char * minUnallowedConsecutiveLength in line:
                line = line.replace(
                    char * minUnallowedConsecutiveLength, char * maxConsecutiveLength
                )
            else:
                break
    return line


def stripChars(line, chars=[" ", "\t"]):
    while True:
        flag = False
        for char in chars:
            if line.startswith(char) or line.endswith(char):
                line = line.strip(char)
                flag = True
        if not flag:
            break
    return line


def standardLineCleaner(line):
    line = removeDuplicates(line)
    line = stripChars(line)
    return line


def getLineWiseAndListOfCleanedMergedConvGroupWithLineIndexMappingFromStringReadFromFile(
    data, char_per_group=30, group_per_conv_group=3, step_group_for_conv=2
):
    # data is the whole string read from file

    data = data.replace("\r\n", "\n")
    # the original data, shall be used as reference. save it somewhere, like database.

    linewise = data.split("\n")  # there won't be "\n" in the line.
    # instead of 1. just to make sure these conv groups overlap.

    assert step_group_for_conv >= 1
    assert (
        step_group_for_conv <= group_per_conv_group
    )  # at least there is no gap, though when equal there will be no overlapping.
    assert group_per_conv_group >= 1
    assert char_per_group >= 1
    # rule to add space: if there's "-" ending, remove the "-" then directly concat with another line.
    # if not, then make sure there's one space between two lines.
    # create char index to line index mapping.

    newContent = ""
    newContentCharIndexToLineIndexDict = {}

    alphabets = "abcdefghijklmnopqrstuvwxyz"
    alphabets += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    import string

    english_punctuation = string.punctuation

    for lineNumber, line in enumerate(linewise):
        line_cleaned = standardLineCleaner(line)
        # for zero length line (after cleaned), we skip without doing anything.
        if len(line_cleaned) == 0:
            continue
        # print("{}:".format(lineNumber), line_cleaned)
        # this process will never decrease the length of the line.
        # i guess the symbol is different somehow. the hyphen is not avaliable on keyboard.
        if line_cleaned.endswith("-") or line_cleaned.endswith("‐"):
            line_cleaned = line_cleaned[:-1]
        elif line_cleaned[-1] in alphabets + english_punctuation:
            line_cleaned += " "
        # we shall get the length again, cause we have processed this thing.
        lineCleanedLength = len(line_cleaned)
        newContentLength = len(newContent)
        mDict = {
            newContentLength + index: lineNumber for index in range(lineCleanedLength)
        }
        newContent += line_cleaned
        newContentCharIndexToLineIndexDict.update(
            mDict
        )  # this shall be the most memory intensive object. delete it after use.

    # now, how to do convolution, or the windowed conv-like excerpt creation?
    # print("MAX KEY:", max(list(newContentCharIndexToLineIndexDict.keys())))
    # MAX KEY: 85783
    # which is smaller than:
    # KeyError: 85830
    # so it is obvious that we need the smaller 'endIndex', by using min(endIndex, newContentLength)
    # breakpoint()

    newContentLength = len(newContent)
    startIndex = 0
    listOfCleanedMergedConvGroupWithLineIndexMapping = []
    # maybe you want to merge the fetched 'cleanedMergedConvGroup' according to 'lineIndexMapping', but that's another story.
    # you can use the mathlib, from pyjom.
    # i think the mathlib should be embedded to lazero. pyjom's mathlib can be grabbed from there.
    while True:
        if startIndex >= newContentLength:  # does not break? wtf?
            break
        endIndexOffset = group_per_conv_group * char_per_group
        endIndex = startIndex + endIndexOffset
        endIndex = min(endIndex, newContentLength - 1)
        # if endIndex <= startIndex:  # failsafe.
        #     continue
        # the append process.
        lineIndexStart = newContentCharIndexToLineIndexDict[
            startIndex
        ]  # maybe not just one line?
        lineIndexEnd = newContentCharIndexToLineIndexDict[endIndex]  # key error? wtf?
        lineIndicesTuple = (lineIndexStart, lineIndexEnd)
        mElem = {
            "conv_group_merged": newContent[startIndex:endIndex],
            "line_range": lineIndicesTuple,
        }
        listOfCleanedMergedConvGroupWithLineIndexMapping.append(
            mElem
        )  # this shall be the thing that we need. just maybe.
        # add to startIndex.
        startIndex += step_group_for_conv * char_per_group

    del newContentCharIndexToLineIndexDict
    return linewise, listOfCleanedMergedConvGroupWithLineIndexMapping


# now we have to process the 'listOfCleanedMergedConvGroupWithLineIndexMapping' list, make each line into 4 corresponding processed line.

# no original line! original line is noisy.
# that is not original line. we need something other than that.

# hint: we do not want to store all these shit in our tiny little memory. we want it 'IN DATABASE'

# from lazero.search.postprocessing import porterStemmer
from nltk.stem import PorterStemmer

porterStemmer = PorterStemmer()  # whill automatically get lower case.
import wordninja
import string
from zhon.hanzi import punctuation as chinese_punctuation
import jieba


def getWordsWithoutPunctuation(line):
    chinese_and_english_punctuation = set(
        list(string.punctuation + chinese_punctuation)
    )
    line = line.replace("\n", " ")
    for punctuation in chinese_and_english_punctuation:
        line = line.replace(punctuation, " ")
    cleaned_line = standardLineCleaner(line)
    # now use what?
    # split with what first?
    # wordninja. split words.
    # nope. we use jieba first.
    jieba_cutted_words = jieba.lcut(cleaned_line)  # remove whitespace!
    final_words = []
    for word in jieba_cutted_words:
        strip_word = word.strip()
        if len(strip_word) == 0:
            # we should only keep the splited words.
            continue
        else:
            final_words.append(word)
    return final_words


def getFourVersionsOfProcessedLine(line, debug=False):
    global porterStemmer
    # from nltk.stem import PorterStemmer
    stemmer = porterStemmer
    final_words = getWordsWithoutPunctuation(line)
    final_cutted_words = []
    for word in final_words:
        ninja_cutted_word = wordninja.split(word)
        if len(ninja_cutted_word) == 0:
            # we shall keep the original word.
            final_cutted_words.append(word)
        else:
            final_cutted_words.extend(ninja_cutted_word)
    # now 'stem' words use nltk.
    final_stemmed_words = [stemmer.stem(word) for word in final_words]
    final_cutted_stemmed_words = [stemmer.stem(word) for word in final_cutted_words]

    # finally, join all things with space, for whatever reason.
    final_line = " ".join(final_words)  # for our dearly transformer
    final_cutted_line = " ".join(final_cutted_words)  # for our dearly whoosh
    final_stemmed_line = " ".join(final_stemmed_words)  # for our dearly whoosh
    final_cutted_stemmed_line = " ".join(
        final_cutted_stemmed_words
    )  # for our dearly whoosh

    # how to use these four things?
    # use them all for all search engines? that will increase our index size significantly!

    # problem is, both query and data need to be processed somehow. but how?

    # you want to use different split methods at the same time, or one at a time?
    # you want to score them right? mostly in whoosh!
    if debug:
        from lazero.utils.logger import sprint

        print("final_line")
        sprint(final_line)
        print("final_cutted_line")
        sprint(final_cutted_line)
        print("final_stemmed_line")
        sprint(final_stemmed_line)
        print("final_cutted_stemmed_line")
        sprint(final_cutted_stemmed_line)
    return final_line, final_cutted_line, final_stemmed_line, final_cutted_stemmed_line


def getFourVersionOfLineInListOfCleanedMergedConvGroupWithLineIndexMapping(
    listOfCleanedMergedConvGroupWithLineIndexMapping, withOriginalLine=False
):
    for elem in listOfCleanedMergedConvGroupWithLineIndexMapping:
        conv_group_merged = elem["conv_group_merged"]
        # what you want to yield?
        (
            final_line,
            final_cutted_line,
            final_stemmed_line,
            final_cutted_stemmed_line,
        ) = getFourVersionsOfProcessedLine(conv_group_merged)
        if withOriginalLine:
            yield conv_group_merged, final_line, final_cutted_line, final_stemmed_line, final_cutted_stemmed_line
        else:
            yield final_line, final_cutted_line, final_stemmed_line, final_cutted_stemmed_line
        # yield (getFourVersionsOfProcessedLine(conv_group_merged),line_range)
