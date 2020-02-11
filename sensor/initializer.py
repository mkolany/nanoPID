import RPi.GPIO as GPIO
import w1thermsensor

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 

heat_pin = 16

GPIO.setup(heat_pin, GPIO.OUT)
heat_pwm = GPIO.PWM(heat_pin, 2)
heat_pwm.start(0)

sensor = w1thermsensor.W1ThermSensor()
value=sensor.get_temperature()
if __name__ == '__main__' :
    print(sensor.get_temperature())