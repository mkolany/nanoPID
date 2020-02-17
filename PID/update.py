import PID.constants
from PID import constrain
import time

ku = 4
pu = 1
kp = 0.45*ku
ki = 1.2*kp/pu
kd = 0

Duty_min=0
Duty_max=100

p_term = 0
i_term = 0 
d_term = 0


def update(old_time, old_error, measured_temp, set_temp):   # (6)
    global p_term, i_term, d_term
    now = time.time()               
    dt = now - old_time # (7)

    error = set_temp - measured_temp # (8)
    de = error - old_error       # (9)

    p_term = kp * error                     # (10)
    i_term += ki * error                    # (11)
    i_term = constrain.constrain(i_term, 0, 100)      # (12)
    d_term = (de / dt) * kd                 # (13)
                                
    old_error = error     
    output = p_term + i_term + d_term      # (14)
    output = constrain.constrain(output, Duty_min, Duty_max)       
    return output
