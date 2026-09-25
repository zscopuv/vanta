from vanta import Console

console = Console()

username = console.ask("Enter username:")
password = console.password(f"Password for [{username}]:")

if username == "admin" and password == "123456789":
    console.success("Logged in")
else:
    console.error("Invalid credentials")