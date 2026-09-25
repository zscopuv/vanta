from vanta import Console

console = Console()

## Version without custom aliases
sports = ["Ice Hockey", "Football", "Volleyball"]
option = console.choose("Pick your sport.", sports)

console.info(f"User picked {option}")


## Version with custom aliases
sports_aliases = {
    "hcky": "Ice Hockey",
    "fb": "Football",
    "vb": "Volleyball"
}
option_aliases = console.choose("Pick your sport.", sports_aliases)

console.info(f"User picked {option_aliases}")