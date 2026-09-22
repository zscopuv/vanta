from vanta import Progress
from time import sleep

test = Progress(
    20,
    label="Downloading"
)

while not test.completed:
    test.update()
    sleep(1)