from pathlib import Path
import re
from typing import TypedDict

class Revisions(TypedDict):
    # The version key represents the current activated version
    # So v1 means v1 is active and the next revision should be v2
    # In order for this to work the number has to be monotonically increasing
    # and have no gaps
    version: int
    database_uri: str
    
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