import asyncio

import click

from kordevance.application.dependencies.gateway_management import get_factory_reset_use_case


@click.command(name="reset", help="Factory reset the gateway")
def reset() -> None:
    click.secho("[CAUTION] This is a destructive action.", fg="yellow", bold=True)
    click.echo(
        "It wipes out the gateway's storage. "
        + click.style("All currently paired clients will be logged out immediately.", bold=True)
        + "\nThis action cannot be undone."
    )
    click.echo()

    answer = click.prompt(
        click.style("Type ", fg="yellow")
        + click.style("RESET", bold=True)
        + click.style(" to confirm, or press Enter to cancel", fg="yellow"),
        default="",
        show_default=False,
    )

    if answer != "RESET":
        raise click.Abort()

    code = asyncio.run(get_factory_reset_use_case().execute())
    if code is None:
        raise click.ClickException("Reset failed: a registered owner was still found after the wipe.")

    click.echo("Claim code: " + click.style(code, fg="yellow", bold=True))
