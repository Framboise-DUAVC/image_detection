import asyncio
import mavsdk
import banners
import trapdoor


async def main():
    # Get drone object and then try to connect
    drone = mavsdk.System()

    # Show info
    print("Trying to connect...")

    # Drone is in serial0
    await drone.connect(system_address="serial:///dev/serial0:921600")

    # Ensure we have future package
    status_text_task = asyncio.ensure_future(print_status_text(drone))

    # Info...
    print("Waiting for drone to connect...")

    # Get connection state
    async for state in drone.core.connection_state():
        if state.is_connected:
            # Info if connected
            print(f"-- Connected to drone!")

            # Show banner
            print(banners.get_px4_banner())

            # Exit async
            break

    # Info...
    # print("-- Arming")
#
    # # Arm
    # await drone.action.arm()

    # Aruco detected info
    print(f"-- Aruco id n {7} detected!")

    # Trapdoor actuation
    await trapdoor.trapdoor_servo_actuator2(drone)

    # Status check
    status_text_task.cancel()


async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


if __name__ == '__main__':
    # Call main running function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
