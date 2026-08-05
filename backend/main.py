"""
=========================================================
sAI V1 - Main Entry Point
=========================================================
Starts the assistant and launches the command interface.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print

from config import (
    ASSISTANT_NAME,
    VERSION,
    BANNER,
)

console = Console()


class SAI:
    def __init__(self):
        self.running = True

    def banner(self):
        console.print(
            Panel.fit(
                f"[bold cyan]{ASSISTANT_NAME}[/bold cyan]\n"
                f"Version {VERSION}\n"
                f"Offline AI Assistant",
                title="Welcome",
                border_style="cyan",
            )
        )

    def help(self):
        print("\n[bold green]Available Commands[/bold green]")
        print("- help")
        print("- about")
        print("- clear")
        print("- exit\n")

    def about(self):
        console.print(
            Panel(
                f"""
Assistant : {ASSISTANT_NAME}
Version   : {VERSION}

sAI V1 is the first version of an offline-first AI assistant.

Features:
• Chat Interface
• Local LLM Support
• Memory
• Voice (Upcoming)
• Vision (Upcoming)
• Automation (Upcoming)
""",
                title="About",
                border_style="green",
            )
        )

    def process(self, command: str):
        cmd = command.strip().lower()

        if cmd == "":
            return

        if cmd == "help":
            self.help()
            return

        if cmd == "about":
            self.about()
            return

        if cmd == "clear":
            console.clear()
            self.banner()
            return

        if cmd == "exit":
            self.running = False
            return

        print(f"\n[cyan]{ASSISTANT_NAME}:[/cyan] I received: [yellow]{command}[/yellow]\n")

    def run(self):
        console.clear()

        print(BANNER)

        self.banner()

        self.help()

        while self.running:
            try:
                command = Prompt.ask("[bold blue]You[/bold blue]")
                self.process(command)

            except KeyboardInterrupt:
                print("\nExiting...")
                break

            except Exception as e:
                print(f"[red]{e}[/red]")

        print("\nGoodbye.\n")


if __name__ == "__main__":
    SAI().run()