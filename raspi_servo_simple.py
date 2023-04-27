import RPi.GPIO
import time

import Logger
import tools


def set_angle(angle, pin_no, pwm):
    duty = (angle / 18) + 2
    RPi.GPIO.output(pin_no, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    RPi.GPIO.output(pin_no, False)
    pwm.ChangeDutyCycle(0)
    return


def main(angle: int = 45, freq: int = 30, wait_time: int = 5, pin_num: int =32, logger: Logger.Logger = None):
    # Other pins: power = 17, ground = 20
    RPi.GPIO.setmode(RPi.GPIO.BOARD)
    RPi.GPIO.setup(pin_num, RPi.GPIO.OUT)

    # Set PWM frequency and pin number
    pwm = RPi.GPIO.PWM(pin_num, freq)

    # Start action
    pwm.start(0)

    # Set the angle
    set_angle(angle, pin_num, pwm)

    # Info
    logger.print_msg(f"Rotating '{angle}' degrees...")

    # Wait some time at that position...
    time.sleep(wait_time)

    # Re-setting to zero
    logger.print_msg("Turning back to 0 degrees...")

    # Re-setting values
    pwm.ChangeDutyCycle(2)

    # Wait again
    time.sleep(1)
    pwm.ChangeDutyCycle(0)

    # Stop
    pwm.stop()

    # Clean stuff
    RPi.GPIO.cleanup()
