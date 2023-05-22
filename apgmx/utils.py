import asyncpg

from .db_settings import database_uri
from .migration import Migrations


async def run_upgrade(migrations: Migrations) -> int:
    connection: asyncpg.Connection = await asyncpg.connect(migrations.database_uri)  # type: ignore
    return await migrations.upgrade(connection)


async def run_upgrade_all(migrations: Migrations) -> int:
    # migrations.database_uri
    connection: asyncpg.Connection = await asyncpg.connect(migrations.database_uri)  # type: ignore
    return await migrations.upgrade_all(connection)


async def ensure_uri_can_run() -> bool:
    connection: asyncpg.Connection = await asyncpg.connect(database_uri)  # type: ignore
    await connection.close()
    return True
