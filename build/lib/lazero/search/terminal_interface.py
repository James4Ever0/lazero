from lazero.search.search import search  # fuck.

# you get input when you hit enter.

from rich.panel import Panel
import textwrap
import os

# import json

# https://github.com/Cvaniak/TextualListViewUnofficial
# the hack
# pip3 install git+https://github.com/Cvaniak/TextualListViewUnofficial.git
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from rich.text import Text

from textual.widgets import ScrollView

from ck_widgets_lv import ListViewUo
from textual_inputs import TextInput
from lazero.search.preprocessing import removeDuplicates

from lazero.search.postprocessing import (
    englishTextToStemmedWords,
    getHighlightedAnswerFromQueryStemmedWordsAndAnswer,
)
from .preprocessing import getFourVersionsOfProcessedLine


class Hover(Widget):

    mouse_over = Reactive(False)

    def __init__(self, *args, **kwargs):
        self.clickFunction = kwargs.pop("onClick", None)
        self.panelStyle = kwargs.pop("panelStyle", "red")
        self.content = kwargs.pop("content", "")
        self.path = kwargs.pop("path", "")
        self.lineNumber = kwargs.pop("lineNumber", 0)
        self.queryStemmedWords = kwargs.pop("queryStemmedWords", [])
        # this need to be retrieved from elsewhere.
        self.score = kwargs.pop("score", 0)
        super().__init__(*args, **kwargs)

    def render(self) -> Panel:
        content = self.content
        text = getHighlightedAnswerFromQueryStemmedWordsAndAnswer(
            self.queryStemmedWords, content
        )
        # we need to render this now.
        size = os.get_terminal_size()
        width = size.columns - 1
        # 80 -> 1
        # 40 -> 2
        # 20 -> 4
        calculatedHeight = 2 + round(80 / width)
        return Panel(
            # this style is strange. we should alter it in some way.
            text,  # you need to stylize the text.
            style=self.panelStyle,
            height=max(3, calculatedHeight),
            title="{:.3f}".format(self.score),
            # title=str(self.score),
            title_align="right",
            subtitle=os.path.basename(self.path),
            subtitle_align="left",
            width=width,  # better config it in some way.
        )  # this is arguable. maybe for mobile device this will be different?
        # calculate this height according to terminal width, and make sure it does not go lower than 3.

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    async def on_click(self):
        if self.clickFunction:
            await self.clickFunction(
                self.path,
                self.lineNumber,
                update=False,  # ensure_visibility=True
            )  # this is not normal clickFunction.


from lazero.search.api import getValueByKeyFromDatabase, lazeroCachePath

# from functools import lru_cache
from lazero.search.postprocessing import getHighlightSetFromQueryStemmedWordsAndAnswer

from lazero.search.api import getLineStartEndInFileByConvLineIndexOriginalFromDatabase


class MyApp(App):
    # how to let me copy the text inslde? fuck?
    # use alt/option key.
    index = 0
    readerName = "viewer"
    content_line_char_count = []
    lineNumbers = []  # are you sure this is the line number you want?
    init = True  # after init (the first search) it shall be set to false!
    noqliteDatabasePath = os.path.join(lazeroCachePath, "lazero_search.db")

    def wrapText(self, textList, width):  # the width is col-1
        content_line_char_count = []
        wrapped_lines = []
        for text in textList:
            lines = textwrap.wrap(text, width=width)
            lineCount = len(lines)
            if lineCount == 0:
                lines = [""]
                lineCount = 1
            content_line_char_count.append(lineCount)
            wrapped_lines.extend(lines)
        return wrapped_lines, content_line_char_count

    async def on_key(self, event):
        key = event.key
        key_lower = key.lower()
        if key_lower == "t":
            # if not self.init:
            await self.mainToggle(toggle=True)
        elif key_lower == "y":
            await self.mainToggle(toggle=True, switchTextInput=False)
        elif key_lower == "j":
            await self.jumpScrollView()
        elif key_lower == "k":
            await self.jumpScrollView(reverse=True)
        elif key_lower == "s":
            await self.focusSearchView()

    async def mainToggle(
        self,
        toggle=False,
        limit: int = 100,
        updateViewer=False,
        updateScrollableHovers=False,
        switchTextInput=True,
        filepath=None,
    ):  # you may need to adjust this thing?
        if toggle:
            if not self.init:
                await self.view.action_toggle("side")
                await self.view.action_toggle("viewer")
                try:
                    if self.body.visible:
                        self.mainInput.subtitle = self.viewerSubtitle
                        if switchTextInput:
                            self.mainInput.value = self.viewerInputText
                    elif self.scrollableHovers.visible:
                        self.mainInput.subtitle = self.scrollableHoverSubtitle
                        if switchTextInput:
                            self.mainInput.value = self.scrollableHoverInputText
                except:
                    ...
                finally:
                    self.mainInput.refresh()
        elif self.init:
            self.init = False
            await self.alterListView(limit=limit)
            # (
            #     self.fileRankList,
            #     self.lineRankListInFileAsDict,
            #     self.lineRankListInAllFiles,
            # ) = self.scrollableHoverRanks
            # self.mainInput.subtitle = self.scrollableHoverSubtitle
        else:  # init starts with the first jump to viewer.
            if self.body.visible or updateViewer:
                await self.alterViewer(filepath, None)
                # (
                #     self.fileRankList,
                #     self.lineRankListInFileAsDict,
                #     self.lineRankListInAllFiles,
                # ) = self.viewerRanks
                # self.mainInput.subtitle = self.viewerSubtitle
            elif self.scrollableHovers.visible or updateScrollableHovers:
                await self.alterListView(limit=limit)
                # (
                #     self.fileRankList,
                #     self.lineRankListInFileAsDict,
                #     self.lineRankListInAllFiles,
                # ) = self.scrollableHoverRanks
                # self.mainInput.subtitle = self.scrollableHoverSubtitle
            # if toggle:

    # you need to specify what to view after the toggle.
    # the viewer. you need to update the file, the line location and other stuff.
    async def updateSearchBoxSubtitle(self, viewer=False):
        if not viewer:
            self.mainInput.subtitle = "{}/{}".format(
                min(self.index + 1, self.totalLineCountInViewer),
                self.totalLineCountInViewer,
            )
        else:
            score = self.viewerLineScores[self.index]
            self.mainInput.subtitle = "{}/{} [{:.3f}]".format(
                self.index + 1, len(self.lineNumbers), score
            )
        self.mainInput.refresh()

    # @lru_cache(maxsize=1)
    def getLineNumbersFromFilePath(self):
        filePath = self.filepath
        lineNumbers = []
        viewerLineScores = []
        # print(self.lineRankListInFileAsDict)
        for elem in self.lineRankListInFileAsDict[filePath]:
            line_index_original = elem["line_index_original"]
            score = elem["score"]
            viewerLineScores.append(score)
            # start_end_json_string = getValueByKeyFromDatabase(
            #     str(line_index_original),
            #     databasePath=self.noqliteDatabasePath,
            # ).decode("utf8")
            # start_end_json = json.loads(start_end_json_string)
            # start = start_end_json[0]  # it is a list. [start, end]
            start, _ = getLineStartEndInFileByConvLineIndexOriginalFromDatabase(
                line_index_original
            )
            # start = start_end_json["start"]
            lineNumbers.append(start)
        self.lineNumbers = lineNumbers
        self.viewerLineScores = viewerLineScores

    async def alterViewer(self, filepath, lineNumber, update=True):
        # print('filepath: ', filepath)
        if self.init:
            self.init = False
        if filepath:
            self.mainInput.value = self.scrollableHoverInputText
        # if ensure_visibility:  # means clicked from listview.
        self.viewerInputText = self.mainInput.value
        # else:
        if update:
            (
                self.fileRankList,
                self.lineRankListInFileAsDict,
                self.lineRankListInAllFiles,
            ) = self.viewerRanks
        # if there is nothing to be displayed what should you emit? i mean inside the file.
        if filepath is not None:
            self.filepath = filepath
        else:
            filepath = self.filepath
        self.getLineNumbersFromFilePath()
        lineNumber = lineNumber if lineNumber is not None else self.lineNumbers[0]
        self.index = self.lineNumbers.index(
            lineNumber
        )  # reset index, after every search.
        # print(self.lineNumbers)
        # self.contentText = contentText
        self.totalLineCountInViewer = len(self.lineNumbers)
        # await self.updateSearchBoxSubtitle()
        await self.updateSearchBoxSubtitle(viewer=True)
        self.viewerSubtitle = self.mainInput.subtitle
        with open(filepath, "r") as f:
            content = f.read()
        # print(content)
        await self.updateViewerContent(content)
        await self.body.update(self.contentText)
        if self.totalLineCountInViewer == 0:
            return
        self.jumpToEquivalentLineNumber(
            self.content_line_char_count, lineNumber  # self.lineNumbers[self.index]
        )
        if not self.body.visible:
            await self.mainToggle(toggle=True)

    async def alterListView(self, limit=100, contentLengthFilter=2):
        if not self.scrollableHovers.visible:
            await self.view.action_toggle("side")
        # if not self.scrollableHovers.visible and not self.init:
        #     return
        # you shall do this for init.
        (
            self.fileRankList,
            self.lineRankListInFileAsDict,
            self.lineRankListInAllFiles,
        ) = self.scrollableHoverRanks
        # if self.init:
        #     self.init = False
        del self.scrollableHovers
        myHoverWidgetList = []
        exceptions = 0
        for rank, element in enumerate(self.lineRankListInAllFiles[:limit]):
            filepath = element["filepath"]
            line_index_original = element["line_index_original"]
            score = element["score"]
            content = getValueByKeyFromDatabase(
                str(line_index_original) + "_content",
                databasePath=self.noqliteDatabasePath,
            ).decode("utf8")
            content = content.strip()
            content = removeDuplicates(content)
            if len(content) < contentLengthFilter:
                exceptions += 1
                continue
            # you also need to highlight these content.
            # highlightSet = getHighlightSetFromQueryStemmedWordsAndAnswer(self.queryStemmedWords, content)
            # highlightWords = list(highlightSet)
            # content = Text(content, style='grey')
            # illegal style. also i don't want this greyish color
            # content = Text(content, style='grey')
            # content.highlight_words(highlightWords, style='yellow')
            start, _ = getLineStartEndInFileByConvLineIndexOriginalFromDatabase(
                line_index_original
            )
            widget = Hover(
                "widget {}_{}_{}".format(
                    line_index_original, filepath, rank
                ),  # this will be the name, but it will not be displayed
                onClick=self.alterViewer,  # toggle what? jump to the viewer?
                lineNumber=start,
                score=score,
                content=content,
                path=filepath,
                queryStemmedWords=self.queryStemmedWords,
            )
            myHoverWidgetList.append(widget)
        self.mainInput.subtitle = str(
            min(len(self.lineRankListInAllFiles) - exceptions, limit)
        )
        self.scrollableHoverSubtitle = self.mainInput.subtitle

        # await self.remove(self.scrollableHovers)
        # try:
        self.scrollableHovers = ListViewUo(myHoverWidgetList)  # what should we update?
        # except:
        #     import traceback
        #     traceback.print_exc()
        #     breakpoint()
        await self.view.action_toggle("side")
        await self.view.dock(self.scrollableHovers, edge="top", name="side")  # WTF?
        # await self.view.action_toggle('side')

    async def action_clearSearchView(self):
        self.mainInput.value = ""

    async def focusSearchView(self):
        # await self.view.action_toggle('search')
        if not self.mainInput.visible:
            await self.view.action_toggle("search")
        await self.mainInput.focus()

    async def jumpScrollView(self, reverse: bool = False):
        if self.body.visible:
            self.index += -1 if reverse else 1
            self.index %= len(self.lineNumbers)
            # print('LINENUMBERS:',self.lineNumbers)
            # print('INDEX',self.index)
            self.jumpToEquivalentLineNumber(
                self.content_line_char_count, self.lineNumbers[self.index]
            )
            await self.updateSearchBoxSubtitle(viewer=True)

    async def updateViewerContent(self, content):
        size = os.get_terminal_size()
        columns, lines = size.columns, size.lines
        textList = content.split("\n")
        wrapped_lines, self.content_line_char_count = self.wrapText(
            textList, columns - 1
        )
        self.wrapped_lines = wrapped_lines
        processed_text = "\n".join(wrapped_lines)
        # but can wrapped lines be highlighted?
        # suck it up. you can't.

        self.contentText = Text(processed_text)
        # highlightLine = "will be efficient. In the example below the recursive call by _range to itself"  # what to highlight? wtf?
        highlightWords = set()
        highlightLines = set()

        for element in self.lineRankListInFileAsDict[self.filepath]:
            line_index_original = element["line_index_original"]
            line = getValueByKeyFromDatabase(
                str(line_index_original) + "_content"
            ).decode("utf-8")
            # start_end_json_string = getValueByKeyFromDatabase(str(line_index_original)).decode('utf-8')
            # start_end_json = json.loads(start_end_json_string)
            # start, end = start_end_json
            start, end = getLineStartEndInFileByConvLineIndexOriginalFromDatabase(
                line_index_original
            )
            wrapped_line_start = sum(self.content_line_char_count[:start])
            wrapped_line_end = sum(self.content_line_char_count[: end + 1])
            # for lineIndex in range(wrapped_line_start, wrapped_line_end + 1):
            for lineIndex in range(wrapped_line_start, wrapped_line_end):
                wrapped_line = wrapped_lines[lineIndex]
                highlightLines.add(wrapped_line)
            highlightSet = getHighlightSetFromQueryStemmedWordsAndAnswer(
                self.queryStemmedWords, line
            )
            highlightWords.update(highlightSet)
        # highlightWord = "recursive"  # maybe not so right.
        # self.contentText.highlight_words([highlightLine], style="red")
        self.contentText.highlight_words(highlightLines, style="red")
        self.contentText.highlight_words(list(highlightWords), style="yellow")

    async def on_load(self) -> None:
        await self.bind("enter", "submit", "Submit")
        await self.bind("ctrl+s", "searchToggle", "searchToggle")
        await self.bind("ctrl+u", "clearSearchView", "clearSearchView")
        await self.bind("escape", "reset_focus", show=False)
        self.body = ScrollView(name=self.readerName)
        # self.height=lines-3

    async def on_mount(self) -> None:
        self.mainInput = TextInput(
            name="searchInput",
            placeholder="enter your query",
            title="lazero search",  # height = 3
        )
        await self.view.dock(self.mainInput, edge="top", size=3, name="search")
        await self.view.dock(
            self.body, edge="top", name="viewer"
        )  # remember that both 'body' and 'ListViewUo' are not visible at the start because there is nothing to display at this time.
        # when search is performed at the first time, 'ListViewUo' shows first.
        # search performed later depends on the visible component, if 'body' is visible then perform search inside this file, if 'ListViewUo' is visible then perform search across multiple files.
        await self.view.action_toggle("viewer")
        self.scrollableHovers = ListViewUo([])

        # changes happens after hitting the enter key, if the search area is cleared, then do nothing.
        await self.view.dock(self.scrollableHovers, edge="top", name="side")
        await self.view.action_toggle("side")
        # this is just init.
        # no content for these right now.
        # do not display them.

    def jumpToEquivalentLineNumber(self, content_line_char_count, lineNumber):
        size = os.get_terminal_size()
        equivalentLineCountPerLine = content_line_char_count

        lineNumber2 = sum(equivalentLineCountPerLine[:lineNumber])
        # lineNumber2 = max(0, lineNumber2-center)
        context = 4  # true context, no extra bullshit. -> real line on rendered result
        lineNumber2 = max(
            0, lineNumber2 - 1 - context
        )  # minus 1 to get the exact line location.
        self.body.set_y(lineNumber2)

    async def action_submit(
        self,
    ):  # limit shall be set to elsewhere, like the update method of
        value = self.mainInput.value
        try:
            value = value.strip()
        except:
            ...
        if not value in ["", None]:
            # do something please?
            queryStemmedWords = set()
            for alteredValue in list(getFourVersionsOfProcessedLine(value)) + [value]:
                for word in englishTextToStemmedWords(alteredValue):
                    queryStemmedWords.add(word)
            self.queryStemmedWords = queryStemmedWords
            filepath = None
            if self.body.visible:
                filepath = self.filepath
            # how to handle this thing?
            (
                fileRankList,
                lineRankListInFileAsDict,
                lineRankListInAllFiles,
            ) = search(value, filter_filepath=filepath)
            # what to do next?
            # notify and execute commands.
            # all two interfaces needs to be updated. the filepath just determines which need to be displayed first.
            if filepath:
                self.viewerRanks = [
                    fileRankList,
                    lineRankListInFileAsDict,
                    lineRankListInAllFiles,
                ]
                # if not self.body.visible:
                self.viewerInputText = self.mainInput.value
                await self.mainToggle()  # toggle what? display what?
            else:
                self.scrollableHoverRanks = [
                    fileRankList,
                    lineRankListInFileAsDict,
                    lineRankListInAllFiles,
                ]
                # if not self.scrollableHovers.visible:
                self.scrollableHoverInputText = self.mainInput.value
                await self.mainToggle()
        self.mainInput.refresh()

    async def action_reset_focus(self):
        if self.body.visible:
            await self.body.focus()
            # add extra elif later
        elif self.scrollableHovers.visible:
            await self.scrollableHovers.focus()
        else:
            await self.view.focus()

    async def action_searchToggle(self):
        await self.view.action_toggle("search")
        if self.mainInput.visible:
            await self.mainInput.focus()
        else:
            await self.view.focus()  # deactivate the search field?


def run():
    MyApp.run()
