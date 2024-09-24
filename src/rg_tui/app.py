import os
from pathlib import Path
from rich.syntax import Syntax
import subprocess
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import (
    Input,
    ListView,
    ListItem,
    DirectoryTree,
    RichLog,
)

from rg_tui.rg import RipGrep


class FilteredDirectoryTree(DirectoryTree):
    _filter: list[Path] | None = None

    def filter_paths(self, paths):
        if self._filter is None:
            return []
        return [path for path in paths if path in self._filter]

    def update_filter(self, paths):
        self._filter = paths
        self.reload()


class MatchListItem(ListItem):
    path: str
    line_number: int

    @classmethod
    def from_match(cls, match):
        log = RichLog()
        context_size = 2
        syntax = Syntax.from_path(
            match.file_path,
            line_numbers=True,
            line_range=(
                match.line_number - context_size,
                match.line_number + context_size,
            ),
            highlight_lines=set([match.line_number]),
        )
        log.write(syntax)
        list_item = cls(log)
        list_item.path = match.file_path
        list_item.line_number = match.line_number
        return list_item


class RgTui(App):
    CSS_PATH = "style.tcss"
    rg: RipGrep | None = None

    def on_mount(self):
        self.rg = RipGrep()

    def compose(self) -> ComposeResult:
        with Container(id="main-grid"):
            yield Input(placeholder="Search pattern", id="pattern_input")
            with Horizontal(id="results"):
                yield FilteredDirectoryTree(".", id="results-tree")
                yield ListView(id="results-context")

    def on_input_changed(self, event: Input.Changed):
        tree = self.query_one(FilteredDirectoryTree)
        lv = self.query_one(ListView)

        self.rg.search(event.value)

        tree.update_filter(self.rg.paths)
        lv.clear()

    def on_directory_tree_file_selected(
        self, event: FilteredDirectoryTree.FileSelected
    ):
        lv = self.query_one(ListView)
        lv.clear()
        lv.extend(
            MatchListItem.from_match(match)
            for match in self.rg.matches[str(event.path)]
        )

    def on_list_view_selected(self, event: ListView.Selected):
        self.exit()
        editor = os.environ.get("EDITOR")
        if editor:
            subprocess.run([editor, "+" + str(event.item.line_number), event.item.path])


if __name__ == "__main__":
    app = MyApp()
    app.run(inline=True)
