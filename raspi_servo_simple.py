import RPi.GPIO
import time

pin = 32
# other pins: power = 17, ground = 20
RPi.GPIO.setmode(RPi.GPIO.BOARD)
RPi.GPIO.setup(pin_no, RPi.GPIO.OUT)
pwm = RPi.GPIO.PWM(pin_no, 50)
pwm.start(0)
sm_angle = 45
actuate = SetAngle(sm_angle, pin)
pwm.stop()
RPi.GPIO.cleanup()
def SetAngle(angle, pin_no):
    duty = (angle / 18) + 2
    RPi.GPIO.output(pin_no, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    RPi.GPIO.output(pin_no, False)
    pwm.ChangeDutyCycle(0)

