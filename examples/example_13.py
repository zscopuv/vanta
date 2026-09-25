from vanta import Console

console = Console()

# If the path does not exist, the user is questioned again.
path = console.path("Where to save the file?", exists=True, directory=True)

console.success(f"File saved as {path}/program.exe")