from vanta import Console

console = Console()

port = console.number(
    "Select the app port:",
    minimum=1,
    maximum=65535,
)

console.info(f"Port {port} will be used.")