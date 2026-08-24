from __future__ import annotations

import logging
from collections.abc import Iterable
from importlib.metadata import PackageNotFoundError, version

import click

from kordevance import _APPLICATION_NAME

COMMANDS: list[click.Command] = []
try:
    from kordevance.cli.commands import COMMANDS
except ImportError:
    pass


class _Palette:
    PRIMARY: str = "cyan"
    MUTED: str = "bright_black"
    SUCCESS: str = "green"
    WARNING: str = "yellow"
    ERROR: str = "red"


class StyledHelpFormatter(click.HelpFormatter):
    def write_usage(self, prog: str, args: str = "", prefix: str | None = None) -> None:
        styled_prefix = click.style("Usage", fg=_Palette.PRIMARY, bold=True) + ": "
        super().write_usage(click.style(prog, bold=True), args, prefix=styled_prefix)

    def write_heading(self, heading: str) -> None:
        super().write_heading(click.style(heading, fg=_Palette.PRIMARY, bold=True))

    def write_dl(self, rows: Iterable[tuple[str, str]], col_max: int = 30, col_spacing: int = 2) -> None:
        styled_rows = [(click.style(term, bold=True), definition) for term, definition in rows]
        super().write_dl(styled_rows, col_max=col_max, col_spacing=col_spacing)


click.Context.formatter_class = StyledHelpFormatter


def _resolve_version() -> str:
    try:
        return version(_APPLICATION_NAME)
    except PackageNotFoundError:
        raise PackageNotFoundError(f"Could not find package {_APPLICATION_NAME}")


__version__: str = _resolve_version()

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 100,
}

_TAGLINE: str = f"Control console of the {_APPLICATION_NAME.upper()} Gateway."


def _print_error(message: str) -> None:
    click.secho("[✖]", fg=_Palette.ERROR, bold=True, nl=False, err=True)
    click.secho(message, fg=_Palette.ERROR, err=True)


_VERSION_MESSAGE = (
    click.style("%(prog)s", fg=_Palette.PRIMARY, bold=True) + " " + click.style("v%(version)s", fg=_Palette.MUTED)
)


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help=click.style(_TAGLINE, fg=_Palette.MUTED),
)
@click.version_option(
    __version__,
    "-v",
    "--version",
    prog_name=_APPLICATION_NAME.upper(),
    message=_VERSION_MESSAGE,
)
@click.pass_context
def main(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


for command in COMMANDS:
    main.add_command(command)


def cli() -> int:
    try:
        main(standalone_mode=False)
        return 0

    except click.ClickException as ce:
        _print_error(ce.format_message())
        return ce.exit_code

    except click.exceptions.Abort:
        click.secho("Aborted.", fg=_Palette.WARNING, err=True)
        return 1

    except SystemExit as se:
        return int(se.code or 0)

    except Exception as e:  # noqa: BLE001
        logging.getLogger(__name__).debug("Unhandled CLI error", exc_info=True)
        _print_error(str(e))
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())
