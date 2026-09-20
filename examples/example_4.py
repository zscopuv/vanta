from vanta import Console


console = Console(
    level="notice"
)

console._testall() # This will not print debug / info (see https://github.com/zscopuv/vanta#log-levels)