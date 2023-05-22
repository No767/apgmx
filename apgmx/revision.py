from pathlib import Path
import re

class Revision:
    __slots__ = ("kind", "version", "description", "file")

    def __init__(
        self, *, kind: str, version: int, description: str, file: Path
    ) -> None:
        self.kind: str = kind
        self.version: int = version
        self.description: str = description
        self.file: Path = file

    @classmethod
    def from_match(cls, match: re.Match[str], file: Path):
        return cls(
            kind=match.group("kind"),
            version=int(match.group("version")),
            description=match.group("description"),
            file=file,
        )