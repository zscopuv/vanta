from vanta import Console


console = Console(
    level="notice"
)

# This will not print debug / info (see https://github.com/zscopuv/vanta#log-levels)
console._testall()