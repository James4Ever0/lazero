
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
text = "myText"*200 # it will be wrapped.
panel = Panel(
            # this style is strange. we should alter it in some way.
            Text(text, style='red'), # you may render this ahead.
            height=4,
            title='0.9', # score.
            title_align='right',
            subtitle='jq_man.log', # which you want first?
            subtitle_align='left',
            style='green'
        )

console = Console()
console.print(panel)