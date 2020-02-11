
def constrain(value, min, max): # (5)
    if value < min :
        return 0
    if value > max :
        return max
    else: 
        return value
    
def update_pid():   # (6)
    global old_time, old_error, measured_temp, set_temp, de
    global p_term, i_term, d_term
    now = time.time()               
    dt = now - old_time # (7)

    error = set_temp - measured_temp # (8)
    de = error - old_error       # (9)

    p_term = kp * error                     # (10)
    i_term += ki * error                    # (11)
    i_term = constrain(i_term, 0, 100)      # (12)
    d_term = (de / dt) * kd                 # (13)
                                
    old_error = error     
    # print((measured_temp, p_term, i_term, d_term))  
    output = p_term + i_term + d_term      # (14)
    output = constrain(output, Duty_min, Duty_max)       
    return output