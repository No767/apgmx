from __future__ import annotations

import datetime
import json
import os
import re

import uuid
from pathlib import Path

import asyncpg
import click

from .revision import Revision
from .types import Revisions
from .constants import REVISION_FILE

class Migrations:
    def __init__(self, *, filename: str = "migrations/revisions.json"):
        self.filename: str = filename
        self.root: Path = Path(filename).parent
        self.revisions: dict[int, Revision] = self.get_revisions()
        self.load()

    def ensure_path(self) -> None:
        self.root.mkdir(exist_ok=True)

    def load_metadata(self) -> Revisions:
        try:
            with open(self.filename, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except FileNotFoundError:
            return {
                "version": 0,
                "database_uri": "None",
            }

    def get_revisions(self) -> dict[int, Revision]:
        result: dict[int, Revision] = {}
        for file in self.root.glob("*.sql"):
            match = REVISION_FILE.match(file.name)
            if match is not None:
                rev = Revision.from_match(match, file)
                result[rev.version] = rev

        return result

    def dump(self) -> Revisions:
        return {
            "version": self.version,
            "database_uri": self.database_uri,
        }

    def load(self) -> None:
        self.ensure_path()
        data = self.load_metadata()
        self.version: int = data["version"]
        self.database_uri: str = data["database_uri"]

    def save(self):
        temp = f"{self.filename}.{uuid.uuid4()}.tmp"
        with open(temp, "w", encoding="utf-8") as tmp:
            json.dump(self.dump(), tmp)

        # atomically move the file
        os.replace(temp, self.filename)

    def is_next_revision_taken(self) -> bool:
        return self.version + 1 in self.revisions

    @property
    def ordered_revisions(self) -> list[Revision]:
        return sorted(self.revisions.values(), key=lambda r: r.version)

    def create_revision(self, reason: str, *, kind: str = "V") -> Revision:
        cleaned = re.sub(r"\s", "_", reason)
        filename = f"{kind}{self.version + 1}__{cleaned}.sql"
        path = self.root / filename

        stub = (
            f"-- Revises: V{self.version}\n"
            f"-- Creation Date: {datetime.datetime.utcnow()} UTC\n"
            f"-- Reason: {reason}\n\n"
        )

        with open(path, "w", encoding="utf-8", newline="\n") as fp:
            fp.write(stub)

        self.save()
        return Revision(
            kind=kind, description=reason, version=self.version + 1, file=path
        )

    async def upgrade(self, connection: asyncpg.Connection) -> int:
        ordered = self.ordered_revisions
        successes = 0
        async with connection.transaction():
            for revision in ordered:
                if revision.version > self.version:
                    sql = revision.file.read_text("utf-8")
                    await connection.execute(sql)
                    successes += 1

        self.version += successes
        self.save()
        return successes

    def display(self) -> None:
        ordered = self.ordered_revisions
        for revision in ordered:
            if revision.version > self.version:
                sql = revision.file.read_text("utf-8")
                click.echo(sql)