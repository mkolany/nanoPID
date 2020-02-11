
def constrain(value, min, max): # (5)
    if value < min :
        return 0
    if value > max :
        return max
    else: 
        return value
