import asyncio
import mavsdk
import time


async def trapdoor_servo_actuator(drone):
    # print current servo position
    print_servo_position_task = asyncio.ensure_future(print_gimbal_position(drone))

    # set control mode of servo to primary
    print("Taking control of trapdoor servo")
    await drone.gimbal.take_control(mavsdk.gimbal.ControlMode.PRIMARY)

    print("Setting servo mode")
    await drone.gimbal.set_mode(mavsdk.gimbal.GimbalMode.YAW_LOCK)

    print("Trapdoor opening...")
    await drone.gimbal.set_pitch_and_yaw(0, 90)  # args are (float pitch_deg, float yaw_deg)
    await asyncio.sleep(5)
    print("Payload dropped!")

    print("Releasing control of trapdoor servo")
    await drone.gimbal.release_control()

    # stop printing current servo position
    print_servo_position_task.cancel()


async def trapdoor_servo_actuator2(drone):
    # print current servo position
    print_servo_position_task = asyncio.ensure_future(print_gimbal_position(drone))

    # set control mode of servo to primary
    print("Taking control of trapdoor servo")
    await drone.action.set_actuator(1, 100)


async def print_gimbal_position(drone):
    # Report gimbal position updates asynchronously in euler angles
    async for angle in drone.telemetry.camera_attitude_euler():
        print("Servo yaw: {angle.yaw_deg}")
