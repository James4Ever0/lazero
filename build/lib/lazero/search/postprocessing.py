# we offer highlight service here. are you sure it will show up in that line? without newline or anything? i mean in the file viewer, not the list view.

# you decide not to remove stopwords?
# it does not affect my highlighting process anyway.


# the order matters!
from lazero.search.preprocessing import getWordsWithoutPunctuation, porterStemmer

# circular import? python does not work for this!


def englishTextToOriginalAndStemmedWordPairs(text):
    global porterStemmer
    doc = getWordsWithoutPunctuation(text)
    # doc = englishNLP(text) # we just want splited words.
    originalAndStemmedWordPairs = []
    for original_word in doc:
        # original_word = token.text
        stemmed_word = porterStemmer.stem(original_word)
        originalAndStemmedWordPairs.append((original_word, stemmed_word))
    return originalAndStemmedWordPairs


def englishTextToStemmedWords(text):
    originalAndStemmedWordPairs = englishTextToOriginalAndStemmedWordPairs(text)
    stemmedWords = [
        stemmed_word for original_word, stemmed_word in originalAndStemmedWordPairs
    ]
    return stemmedWords


# it needs 'query'
# do it in batch or do it in series.
# query =
# answers =
# queryStemmedWords = englishTextToStemmedWords(query) # we use this as input, not the query itself.
# named as such, but this process is universal, not just for english.
# maybe we don't have to invent this shit again.
def getHighlightSetFromQueryStemmedWordsAndAnswer(queryStemmedWords, answer):
    highlightSet = set()
    answerOriginalAndStemmedWordPairs = englishTextToOriginalAndStemmedWordPairs(answer)
    for original_word, stemmed_word in answerOriginalAndStemmedWordPairs:
        if stemmed_word in queryStemmedWords:
            highlightSet.add(
                original_word
            )  # just original_word is enough. remember to deduplicate.
    return highlightSet


def getHighlightedAnswerFromQueryStemmedWordsAndAnswer(
    queryStemmedWords, answer, debug=False
):
    # parse and stem both query and answer, check for commondities.
    # sentence -> [(original_word, stemmed_word), ...]

    # we need to show these highlights! fuck.
    if debug:
        from lazero.utils.logger import sprint

        # sprint("QUERY:", query)
        sprint("QUERY KEYWORDS STEMMED:", queryStemmedWords)

    from rich.text import Text

    text = Text(answer,style='white')
    # text = Text(answer, style="gray")  # there is no style applied.
    highlightSet = getHighlightSetFromQueryStemmedWordsAndAnswer(
        queryStemmedWords, answer
    )
    text.highlight_words(
        highlightSet, style="yellow"
    )  # but we should not highlight individual letters right?
    if debug:
        from rich.console import Console

        console = Console()
        console.print(text)
    return text
