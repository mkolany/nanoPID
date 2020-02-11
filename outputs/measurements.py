# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import w1thermsensor
import time
import csv
import matplotlib.pyplot as plt

## pin setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 

heat_pin = 16

GPIO.setup(heat_pin, GPIO.OUT)
heat_pwm = GPIO.PWM(heat_pin, 2)
heat_pwm.start(0)

sensor = w1thermsensor.W1ThermSensor()

## variables
Duty_min=0
Duty_max=100
set_temp = 30

Temp_lista=[]
Duty_lista=[]

old_error = 0 
old_time = 0
measured_temp = 0
p_term = 0
i_term = 0 
d_term = 0

#### plikozapisywcz
f = open('outputs/'+str(int(time.time()))+'.csv', 'w', newline='')
writer = csv.writer(f,  delimiter=',')
    
def zapisz(measured_temp, duty, set_temp):
    writer.writerow([measured_temp, duty, set_temp])
    
#### pid

ku = 4
pu = 1
kp = 0.45*ku
ki = 1.2*kp/pu
kd = 0

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

print("Duty range: [%d, %d]"%(Duty_min, Duty_max))

print("PID constants: Kp=%d, Ki=%d, Kd=%d"%(kp,ki,kd))

print("Set temperature: ",set_temp)

zapisz(0,0,0) # testowy zapis

input("\nPress enter to continue\r")

old_time = time.time()
try:         
    while True:
     
        # pomiar temperatury (co 1000 ms)
        now = time.time()*1000.0
        if now > old_time + 1:
            old_time = now
            measured_temp = sensor.get_temperature()
            
            duty = update_pid()
            heat_pwm.ChangeDutyCycle(duty)

            Temp_lista.append(measured_temp)
            Duty_lista.append(duty)
            zapisz(measured_temp, duty, set_temp) # zapisanie do csv

            print('Temp: %s    Duty: %f\r'%(measured_temp,duty), end="")

       
finally:
    GPIO.cleanup()
    heat_pwm.ChangeDutyCycle(0)


    fig, ax = plt.subplots(2,1)
    ax[0].set_ylabel('Temperature [°C]')

    ax[1].set_xlabel('Time [s]')
    ax[1].set_ylabel('PWM duty')

    ax[1].set_ylim([0,100])
    
    ax[0].plot(Temp_lista, color='black', label='Measured temperature')
    ax[0].axhline(set_temp, color='red', label='Set temperature')
    ax[0].legend()

    ax[1].plot(Duty_lista, color='olive', label='Duty')
    ax[1].legend()
    
    fig.savefig('outputs/'+str(int(time.time()))+'.png')
