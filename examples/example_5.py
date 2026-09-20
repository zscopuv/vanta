from time import sleep

from vanta import Timer


timer = Timer(autostart=True)

sleep(1.525)

timer.stop()  # Optional, but recommended

print(timer.elapsed)  # Around 1.525 sec
print(timer.ms)       # Around 1525 ms