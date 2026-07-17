from rich.console import Console
from rich.panel import Panel

from lucy.ui.theme import SUCCESS, ERROR, WARNING, PRIMARY, DEFAULT
from lucy.ui.constants import TICK, CROSS, CAUTION, MISSING


class DoctorUI:
    def __init__(self, console: Console):
        self.console = console

    def render_doctor_flow(self):
        from lucy.cli.doctor import run_doctor
        self.console.print(
            Panel.fit(
                f"[{DEFAULT}]Running installation diagnostics...[{DEFAULT}]",
                title="Lucy Doctor",
                style=PRIMARY
            )
        )
        self.console.print()

        passed = failed = warnings = skipped = 0

        STATUS = {
            "passed": f"[{SUCCESS}]{TICK}[/]",
            "failed": f"[{ERROR}]{CROSS}[/]",
            "warning": f"[{WARNING}]{CAUTION}[/]",
            "skipped": MISSING,
        }

        for event in run_doctor():
            self.console.print(
                f"{STATUS[event.status]} [bold]{event.name:<18}[/bold] [dim]{event.details}[/dim]"
            )

            match event.status:
                case "passed":
                    passed += 1

                case "failed":
                    failed += 1

                    if event.fix:
                        self.console.print(
                            f"   [bold {ERROR}]Fix:[/] {event.fix}"
                        )

                    self.console.print()

                case "warning":
                    warnings += 1

                    if event.fix:
                        self.console.print(
                            f"   [{WARNING}]Tip:[/] {event.fix}"
                        )

                    self.console.print()

                case "skipped":
                    skipped += 1
                    self.console.print()

        self.console.rule()

        total = passed + warnings + skipped + failed

        self.console.print("[bold]Summary[/bold]\n")
        self.console.print(f"Doctor ran {total} health checks.\n")

        self.console.print(
            f"[{SUCCESS}]{TICK}[/] Passed: {passed}"
        )

        if warnings:
            self.console.print(
                f"[{WARNING}]{CAUTION}[/] Warnings: {warnings}"
            )

        if skipped:
            self.console.print(
                f"{MISSING} Skipped: {skipped}"
            )

        if failed:
            self.console.print(
                f"[{ERROR}]{CROSS}[/] Failed: {failed}"
            )

        self.console.print()

        if failed:
            self.console.print(
                f"[bold {ERROR}]Lucy is not ready to use.[/bold {ERROR}]"
            )
        elif warnings:
            self.console.print(
                f"[bold {WARNING}]Lucy is ready to use.\nReview the warnings above for the best experience.[/bold {WARNING}]"
            )
        else:
            self.console.print(
                f"[bold {SUCCESS}]Lucy is ready to use![/bold {SUCCESS}]"
            )
        self.console.print()