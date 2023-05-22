from .constants import POSTGRES_URL
import asyncpg
import click

from .migration import Migrations
import asyncio
import traceback


@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
def main():
    """Launches the bot."""
    pass
    # if ctx.invoked_subcommand is None:
    #     with setup_logging():
    #         asyncio.run(run_bot())


@main.group(short_help="database stuff", options_metavar="[options]")
def db():
    pass


async def ensure_uri_can_run() -> bool:
    connection: asyncpg.Connection = await asyncpg.connect(POSTGRES_URL)
    await connection.close()
    return True


@db.command()
@click.option(
    "--reason", "-r", help="The reason for this revision.", default="Initial migration"
)
def init(reason):
    """Initializes the database and creates the initial revision."""

    asyncio.run(ensure_uri_can_run())

    migrations = Migrations()
    migrations.database_uri = POSTGRES_URL  # type: ignore
    # migrations.database_uri = ""
    revision = migrations.create_revision(reason)
    click.echo(f"created revision V{revision.version!r}")
    click.secho(f"hint: use the `upgrade` command to apply", fg="yellow")


@db.command()
@click.option("--reason", "-r", help="The reason for this revision.", required=True)
def migrate(reason):
    """Creates a new revision for you to edit."""
    migrations = Migrations()
    if migrations.is_next_revision_taken():
        click.echo(
            "an unapplied migration already exists for the next version, exiting"
        )
        click.secho(
            "hint: apply pending migrations with the `upgrade` command", bold=True
        )
        return

    revision = migrations.create_revision(reason)
    click.echo(f"Created revision V{revision.version!r}")


async def run_upgrade(migrations: Migrations) -> int:
    connection: asyncpg.Connection = await asyncpg.connect(migrations.database_uri)  # type: ignore
    return await migrations.upgrade(connection)


@db.command()
@click.option("--sql", help="Print the SQL instead of executing it", is_flag=True)
def upgrade(sql):
    """Upgrades the database at the given revision (if any)."""
    migrations = Migrations()

    if sql:
        migrations.display()
        return

    try:
        applied = asyncio.run(run_upgrade(migrations))
    except Exception:
        traceback.print_exc()
        click.secho("failed to apply migrations due to error", fg="red")
    else:
        click.secho(f"Applied {applied} revisions(s)", fg="green")


@db.command()
def current():
    """Shows the current active revision version"""
    migrations = Migrations()
    click.echo(f"Version {migrations.version}")


@db.command()
@click.option("--reverse", help="Print in reverse order (oldest first).", is_flag=True)
def log(reverse):
    """Displays the revision history"""
    migrations = Migrations()
    # Revisions is oldest first already
    revs = (
        reversed(migrations.ordered_revisions)
        if not reverse
        else migrations.ordered_revisions
    )
    for rev in revs:
        as_yellow = click.style(f"V{rev.version:>03}", fg="yellow")
        click.echo(f'{as_yellow} {rev.description.replace("_", " ")}')


if __name__ == "__main__":
    main()