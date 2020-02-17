# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import w1thermsensor
import time
import csv


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
Duty_max=50
set_temp = 30

Temp_lista=[]
Duty_lista=[]
Tset_lista=[]

old_error = 0 
old_time = 0
measured_temp = 0
Mvolt = ''
Mresi = ''

p_term = 0
i_term = 0 
d_term = 0


    
#### pid

kp = 3
ki = 0.01
kd = 0.02

#### eps

EPSILON = 1

############ FUNKCJE ################################

#### plikozapisywcz
f = open('/home/pi/Documents/python/outputs/'+str(int(time.time()))+'.csv', 'w', newline='')
writer = csv.writer(f,  delimiter=',')
    
def zapisz(measured_temp, duty, set_temp, Mvolt, Mresi):
    writer.writerow([measured_temp, duty, set_temp, Mvolt, Mresi])


### ogranicza maksymalny PWM

def constrain(value, min, max): # (5)
    if value < min :
        return 0
    if value > max :
        return max
    else: 
        return value

### obliczanie PID
    
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

### Keithley

def beep(notes):
	noteToHz = {
		'A': 440,
		'B': 493.88,
		'C': 523.25,
		'D': 587.33,
		'E': 659.25,
		'F': 698.46,
		'G': 783.99
	}
	for note in notes:
		Keithley.write('SYSTEM:BEEP %s,0.1' %noteToHz.get(str(note).upper(), '20'))

def voltMeas():
	Keithley.write('SENSE:FUNCTION "VOLTAGE"')
	Keithley.write('SENSE:VOLTAGE:RSENSE ON')
	Keithley.write('OUTPUT:STATE ON')
	Keithley.write('COUNT 1')
	
	Keithley.query('READ? "voltMeasBuffer", FORM, DATE, READ')

	return (Keithley.query('TRAC:DATA? 1, 1, "voltMeasBuffer", READING'))

def resMeas():
	Keithley.write('SENSE:FUNCTION "RESISTANCE"')
	Keithley.write('SENSE:RESISTANCE:RSENSE ON')
	Keithley.write('OUTPUT ON')
	Keithley.write('COUNT 1')
	

	
	Keithley.query('READ? "ohmMeasBuffer", FORM, DATE, READ')

	Keithley.write('OUTPUT OFF')
	return (Keithley.query('TRAC:DATA? 1, 1, "ohmMeasBuffer", READING'))

########## START ######################################

# podłączanie KEITHLEY
print("Loading visa package (it takes a while)")
import visa 

print("Connecting to a device\n")
rm = visa.ResourceManager('@py')
Keithley = rm.open_resource('USB0::1510::9296::04384536::0::INSTR')
Keithley.timeout = None

beep('C')

print(Keithley.query('*IDN?'))

print("\nSetting it up (this is quite fast)")

Keithley.write('*RST') 

Keithley.write('TRACe:MAKE "voltMeasBuffer", 10')
Keithley.write('TRACE:FILL:MODE CONT, "voltMeasBuffer"')
Keithley.write('TRACe:MAKE "ohmMeasBuffer", 10')
Keithley.write('TRACE:FILL:MODE CONT, "ohmMeasBuffer"')


beep('CEC')
input('Proceed?')

#
print("Duty range: [%d, %d]"%(Duty_min, Duty_max))

print("PID constants: Kp=%f, Ki=%f, Kd=%f"%(kp,ki,kd))

print("Set temperature: ",set_temp)

zapisz('','','','','') # testowy zapis

input("\nPress enter to continue\r")

old_time = time.time()
old_time2 = time.time()
try:         
    while True:

        if set_temp < 201 :
            # pomiar temperatury (co 1000 ms)
            now = time.time()
            if now > old_time + 1:
                old_time = now
                measured_temp = sensor.get_temperature()
                
                duty = update_pid()
                heat_pwm.ChangeDutyCycle(duty)

                Temp_lista.append(measured_temp)
                Duty_lista.append(duty)
                Tset_lista.append(set_temp)

                zapisz(measured_temp, duty, set_temp, Mvolt, Mresi) # zapisanie do csv
                Mvolt = ''
                Mresi = ''

                print('Set temp: %s    Measured temp: %s    Duty: %f\r'%(set_temp,measured_temp,duty), end="")

            if all(abs(temp-set_temp)<EPSILON for temp in Temp_lista[-10:]):
                if now > old_time2 + 30:
                	old_time2 = now

                	Mvolt=voltMeas()
                	Mresi=resMeas()
	                
	                beep('COC')

	                set_temp = set_temp + 10
            else:
                old_time2=now


       
finally:
    GPIO.cleanup()
    heat_pwm.ChangeDutyCycle(0)