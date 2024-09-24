from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass
class Match:
    file_path: str
    line_number: int
    line_content: str


class RipGrep:
    matches: dict[str, list[Match]]
    paths: set[Path]

    def __init__(self):
        self.matches = defaultdict(list)
        self.paths = set()

    def clear(self):
        self.matches = defaultdict(list)
        self.paths = set()

    def search(self, pattern: str):
        output = self.ripgrep(pattern)

        self.clear()

        if output is None:
            return

        for line in output.split("\n"):
            if not line:
                continue

            file_path, line_number, content = line.split(":", 2)

            path = Path(file_path).resolve()
            match = Match(
                file_path=file_path,
                line_number=int(line_number),
                line_content=content,
            )

            self.matches[str(path)].append(match)

            self.paths.add(path)
            for parent in path.parents:
                self.paths.add(parent)

    @staticmethod
    def ripgrep(pattern, path="."):
        if not pattern:
            return None

        try:
            command = ["rg", "--line-number", pattern, path]

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"ripgrep error: {e.stderr}")
            return None
