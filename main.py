# -*- coding: utf-8 -*-
import settings
import sensor.initializer

import time
import csv
import matplotlib.pyplot as plt


#### plikozapisywcz
f = open('outputs/'+str(int(time.time()))+'.csv', 'w', newline='')
writer = csv.writer(f,  delimiter=',')
    
def zapisz(measured_temp, duty, set_temp):
    writer.writerow([measured_temp, duty, set_temp])
    
#### pid

from PID import update
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


ku = 4
pu = 1
kp = 0.45*ku
ki = 1.2*kp/pu
kd = 0

print("Duty range: [%d, %d]"%(Duty_min, Duty_max))

print("PID constants: Kp=%d, Ki=%d, Kd=%d"%(kp,ki,kd))

print("Set temperature: ",set_temp)

zapisz(0,0,0) # testowy zapis

input("\nPress enter to continue\r")

old_time = time.time()*1000.0
old_time2 = time.time()*1000.0

try:         
    while True:

        if set_temp < 201 :
            # pomiar temperatury (co 1000 ms)
            now = time.time()*1000.0
            if now > old_time + 1:
                old_time = now
                measured_temp = sensor.initializer.value
                
                duty = update.update(old_time, old_error, measured_temp, set_temp)
                heat_pwm.ChangeDutyCycle(duty)

                Temp_lista.append(measured_temp)
                Duty_lista.append(duty)
                zapisz(measured_temp, duty, set_temp) # zapisanie do csv

                print('Set temp: %s    Measured temp: %s    Duty: %f\r'%(set_temp,measured_temp,duty), end="")

            if now > old_time2 + 5:
                old_time2=now
                set_temp = set_temp + 10


       
finally:
    sensor.initializer.GPIO.cleanup()
    sensor.initializer.heat_pwm.ChangeDutyCycle(0)


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
