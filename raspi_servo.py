import RPi.GPIO as GPIO
import time


def command_servo(pin_place: int, frequency: float):
    # Set everything up
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_place, GPIO.OUT)
    servo = GPIO.PWM(pin_place, frequency)

    # Servo start 0 TODO: Why? @Krishna answer this
    servo.start(0)

    # Info
    print("Rotating at intervals of 12 degrees")

    # Duty: time signal is up
    duty = 2
    while duty <= 17:
        servo.ChangeDutyCycle(duty)
        time.sleep(1)
        duty = duty + 1

    # Re-setting back to zero
    print("Turning back to 0 degrees")
    servo.ChangeDutyCycle(2)
    time.sleep(1)
    servo.ChangeDutyCycle(0)

    # Stop
    servo.stop()
    GPIO.cleanup()

    # Print
    print("Everything's cleaned up")
