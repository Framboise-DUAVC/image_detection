import RPi.GPIO
import time


def set_angle(angle, pin_no):
    duty = (angle / 18) + 2
    RPi.GPIO.output(pin_no, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    RPi.GPIO.output(pin_no, False)
    pwm.ChangeDutyCycle(0)
    return


pin = 32
# other pins: power = 17, ground = 20
RPi.GPIO.setmode(RPi.GPIO.BOARD)
RPi.GPIO.setup(pin, RPi.GPIO.OUT)
pwm = RPi.GPIO.PWM(pin, 30)
pwm.start(0)
sm_angle = 45
set_angle(sm_angle, pin)
pwm.stop()
RPi.GPIO.cleanup()
