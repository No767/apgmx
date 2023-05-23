import asyncpg

from .config_loader import ConfigLoader
from .migration import Migrations

confLoader: ConfigLoader = ConfigLoader()


async def run_upgrade(migrations: Migrations) -> int:
    connection: asyncpg.Connection = await asyncpg.connect(
        confLoader.get_database_uri()
    )
    return await migrations.upgrade(connection)


async def run_upgrade_all(migrations: Migrations) -> int:
    connection: asyncpg.Connection = await asyncpg.connect(confLoader.get_database_uri())  # type: ignore
    return await migrations.upgrade_all(connection)


async def ensure_uri_can_run(confLoader: ConfigLoader) -> bool:
    connection: asyncpg.Connection = await asyncpg.connect(confLoader.get_database_uri())  # type: ignore
    await connection.close()
    return True
