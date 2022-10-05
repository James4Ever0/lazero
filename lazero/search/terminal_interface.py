from lazero.search.search import search  # fuck.

# you get input when you hit enter.

from rich.panel import Panel
import textwrap
import os
import json

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

from lazero.search.postprocessing import (
    englishTextToStemmedWords,
    getHighlightedAnswerFromQueryStemmedWordsAndAnswer,
)


class Hover(Widget):

    mouse_over = Reactive(False)

    def __init__(self, *args, **kwargs):
        self.clickFunction = kwargs.pop("onClick", None)
        self.panelStyle = kwargs.pop("panelStyle", "")
        self.content = kwargs.pop("content", "")
        self.path = kwargs.pop("path", "")
        self.queryStemmedWords = kwargs.pop("queryStemmedWords", [])
        # this need to be retrieved from elsewhere.
        self.score = kwargs.pop("score", 0)
        super().__init__(*args, **kwargs)

    def render(self) -> Panel:
        text = getHighlightedAnswerFromQueryStemmedWordsAndAnswer(
            self.queryStemmedWords, self.content
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
            title=str(self.score),
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
                self.path, ensure_visibility=True
            )  # this is not normal clickFunction.


from lazero.search.api import getValueByKeyFromDatabase, lazeroCachePath
from functools import lru_cache
from lazero.search.postprocessing import getHighlightSetFromQueryStemmedWordsAndAnswer


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
            await self.mainToggle()
        elif key_lower == "j":
            await self.jumpScrollView()
        elif key_lower == "k":
            await self.jumpScrollView(reverse=True)
        elif key_lower == "s":
            await self.focusSearchView()

    async def mainToggle(self):  # you may need to adjust this thing?
        if not self.init:  # init starts with the first jump to viewer.
            await self.view.action_toggle("side")
            await self.view.action_toggle("viewer")
            if self.body.visible:
                (
                    self.fileRankList,
                    self.lineRankListInFileAsDict,
                    self.lineRankListInAllFiles,
                ) = self.viewerRanks
                self.mainInput.subtitle = self.viewerSubtitle
            elif self.scrollableHovers.visible:
                (
                    self.fileRankList,
                    self.lineRankListInFileAsDict,
                    self.lineRankListInAllFiles,
                ) = self.scrollableHoverRanks
                self.mainInput.subtitle = self.scrollableHoverSubtitle

    # you need to specify what to view after the toggle.
    # the viewer. you need to update the file, the line location and other stuff.
    async def updateSearchBoxSubtitle(self):
        self.mainInput.subtitle = "{}/{}".format(
            min(self.index + 1, self.totalLineCountInViewer),
            self.totalLineCountInViewer,
        )

    @lru_cache(maxsize=1)
    def getLineNumbersFromFilePath(self):
        filePath = self.filepath
        lineNumbers = []
        for elem in self.lineRankListInFileAsDict[filePath]:
            line_index_original = elem["line_index_original"]
            start_end_json_string = getValueByKeyFromDatabase(
                str(line_index_original),
                databasePath=self.noqliteDatabasePath,
            ).decode("utf8")
            start_end_json = json.loads(start_end_json_string)
            start = start_end_json["start"]
            lineNumbers.append(start)
        self.lineNumbers = lineNumbers

    async def alterViewer(self, filepath, ensure_visibility=False):
        if not self.init:
            self.init = True
        if ensure_visibility:  # means clicked from listview.
            if not self.body.visible:
                await self.mainToggle()
        else:
            (
                self.fileRankList,
                self.lineRankListInFileAsDict,
                self.lineRankListInAllFiles,
            ) = self.viewerRanks
        self.index = 0  # reset index, after every search.
        # if there is nothing to be displayed what should you emit? i mean inside the file.
        self.filepath = filepath
        self.getLineNumbersFromFilePath()
        # self.contentText = contentText
        self.totalLineCountInViewer = len(self.lineNumbers)
        await self.updateSearchBoxSubtitle()
        self.viewerSubtitle = self.mainInput.subtitle
        await self.body.update(self.contentText)
        if self.totalLineCountInViewer == 0:
            return
        with open(filepath, "r") as f:
            content = f.read()
        await self.updateViewerContent(content)
        self.jumpToEquivalentLineNumber(
            self.content_line_char_count, self.lineNumbers[self.index]
        )

    async def alterListView(self, limit=100):
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
        self.mainInput.subtitle = str(min(len(self.lineRankListInAllFiles), limit))
        self.scrollableHoverSubtitle = self.mainInput.subtitle

        for rank, element in enumerate(self.lineRankListInAllFiles[:limit]):
            filepath = element["filepath"]
            line_index_original = element["line_index_original"]
            score = element["score"]
            content = getValueByKeyFromDatabase(
                str(line_index_original) + "_content",
                databasePath=self.noqliteDatabasePath,
            ).decode("utf8")
            widget = Hover(
                "widget {}_{}_{}".format(
                    line_index_original, filepath, rank
                ),  # this will be the name, but it will not be displayed
                onClick=self.alterViewer,  # toggle what? jump to the viewer?
                score=score,
                content=content,
                path=filepath,
                queryStemmedWords=self.queryStemmedWords,
            )
            myHoverWidgetList.append(widget)

        # await self.remove(self.scrollableHovers)
        self.scrollableHovers = ListViewUo(myHoverWidgetList)  # what should we update?
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
            self.index += -int(reverse)
            self.index %= len(self.lineNumbers)
            self.jumpToEquivalentLineNumber(
                self.content_line_char_count, self.lineNumbers[self.index]
            )

    async def updateViewerContent(self, content):
        size = os.get_terminal_size()
        columns, lines = size.columns, size.lines
        textList = content.split("\n")
        wrapped_lines, self.content_line_char_count = self.wrapText(
            textList, columns - 1
        )
        processed_text = "\n".join(wrapped_lines)
        # but can wrapped lines be highlighted?
        # suck it up. you can't.

        self.contentText = Text(processed_text)
        # highlightLine = "will be efficient. In the example below the recursive call by _range to itself"  # what to highlight? wtf?
        highlightWords = set()

        for element in self.lineRankListInFileAsDict[self.filepath]:
            line_index_original = element["line_index_original"]
            line = getValueByKeyFromDatabase(
                str(line_index_original) + "_content"
            ).decode("utf-8")
            highlightSet = getHighlightSetFromQueryStemmedWordsAndAnswer(
                self.queryStemmedWords, line
            )
            highlightWords.update(highlightSet)
        # highlightWord = "recursive"  # maybe not so right.
        # self.contentText.highlight_words([highlightLine], style="red")
        self.contentText.highlight_words(highlightWords, style="yellow")

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
        self.scrollableHovers = ListViewUo()

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
            self.queryStemmedWords = englishTextToStemmedWords(value)
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
                if not self.body.visible:
                    await self.mainToggle()
            else:
                self.scrollableHoverRanks = [
                    fileRankList,
                    lineRankListInFileAsDict,
                    lineRankListInAllFiles,
                ]
                if not self.scrollableHovers.visible:
                    await self.mainToggle()

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
