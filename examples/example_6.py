
import time
from vanta import Timer

timer = Timer(autostart=True) # Timer started

time.sleep(1)           # +1000 ms

timer.pause()           # Timer paused. Total = 1000ms

time.sleep(2)           # +0 ms (timer.paused = True)

timer.unpause()         # Timer unpaused. Total = 1000ms

time.sleep(1)           # +1000 ms

timer.stop()            # Timer stopped. Total = 2000ms

print(timer.ms)