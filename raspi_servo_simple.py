import RPi.GPIO
import time

import tools


def set_angle(angle, pin_no):
    duty = (angle / 18) + 2
    RPi.GPIO.output(pin_no, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    RPi.GPIO.output(pin_no, False)
    pwm.ChangeDutyCycle(0)
    return


def main(angle: int = 90, freq: int = 30, wait_time: int = 10, pin_num: int =32, verbose: bool = False):
    # Other pins: power = 17, ground = 20
    RPi.GPIO.setmode(RPi.GPIO.BOARD)
    RPi.GPIO.setup(pin_num, RPi.GPIO.OUT)

    # Set PWM frequency and pin number
    pwm = RPi.GPIO.PWM(pin_num, freq)

    # Start action
    pwm.start(0)

    # Set the angle
    set_angle(angle, pin_num)

    # Info
    tools.print_msg(f"Rotating '{}'...", verbose=verbose)

    # Wait some time at that position...
    time.sleep(wait_time)

    # Re-setting to zero
    tools.print_msg("Turning back to 0 degrees...", verbose=verbose)

    # Re-setting values
    pwm.ChangeDutyCycle(2)

    # Wait again
    time.sleep(1)
    pwm.ChangeDutyCycle(0)

    # Stop
    pwm.stop()
