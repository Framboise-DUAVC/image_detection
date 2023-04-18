import asyncio
import mavsdk
import banners
import datetime

import photographer


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

    # Info
    print("Waiting for drone to have a global position estimate...")

    # Check GPS
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            # Info
            print("-- Global position estimate OK")

            # Exit async
            break

    # Info...
    print("-- Arming")

    # Arm
    await drone.action.arm()

    # Info
    print("-- Taking off")

    # Take off
    await drone.action.takeoff()

    # Info
    print("-- Waiting for cruise altitude...")

    # Get the flight mode
    async for flight_mode in drone.telemetry.flight_mode():

        # Display flight mode
        print(f"-- FlightMode: {str(flight_mode)}")

        # TODO: Change here what the mode will be when starting to do photos
        if str(flight_mode).strip().lower() == "hold":
            # Show info
            print("-- Starting photographer...")

            # TODO: Call the photographer here
            # Get time formatted as a string
            mission_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Prepare arguments for photographer
            detection_args = ["dummy",
                "--max_time",   "3600",                       # time [seconds]
                "--output",     f"~/mission_{mission_time}",    #
                "--mission",    "true", #
                "--verbose",    "true"  #
            ]

            # Call to main photographer detector
            photographer.main(detection_args)

            break

    # Aruco detected info
    print(f"-- Aruco id n {7} detected!")

    # Trapdoor actuation
    trapdoor.trapdoor_servo_actuator(drone)

    # Landing
    print("-- Landing")
    await drone.action.land()

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
