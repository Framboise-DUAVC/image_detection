import asyncio
import mavsdk
import banners
import datetime

import photographer
import tools
import raspi_servo_simple


async def main(verbose: bool = True):
    # Get drone object and then try to connect
    drone = mavsdk.System()

    # Show info
    tools.print_msg("Trying to connect...", verbose=verbose)

    # Drone is in serial0
    await drone.connect(system_address="serial:///dev/serial0:921600")

    # Ensure we have future package
    status_text_task = asyncio.ensure_future(print_status_text(drone, verbose=verbose))

    # Info...
    tools.print_msg("Waiting for drone to connect...", verbose=verbose)

    # Get connection state
    async for state in drone.core.connection_state():
        if state.is_connected:
            # Info if connected
            tools.print_msg(f"-- Connected to drone!", verbose=verbose)

            # Show banner
            tools.print_msg(f"{banners.get_px4_banner()}", verbose=verbose)

            # Exit async
            break

    # Info
    tools.print_msg("Waiting for drone to have a global position estimate...", verbose=verbose)

    # Check GPS
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            # Info
            tools.print_msg("-- Global position estimate OK", verbose=verbose)

            # Exit async
            break

    # Info...
    tools.print_msg("-- Arming", verbose=verbose)

    # Arm
    await drone.action.arm()

    # Info
    tools.print_msg("-- Taking off", verbose=verbose)

    # Take off
    await drone.action.takeoff()

    # Info
    tools.print_msg("-- Waiting for cruise altitude...", verbose=verbose)

    # Get the flight mode
    async for flight_mode in drone.telemetry.flight_mode():

        # Display flight mode
        tools.print_msg(f"-- FlightMode: {str(flight_mode)}", verbose=verbose)

        # TODO: Change here what the mode will be when starting to do photos
        if str(flight_mode).strip().lower() == "hold":
            # Show info
            tools.print_msg("-- Starting photographer...", verbose=verbose)

            # Call to detection and action
            detection_and_action(verbose=verbose)

            break

    # Landing
    tools.print_msg("-- Landing", verbose=verbose)
    await drone.action.land()

    # Status check
    status_text_task.cancel()


def detection_and_action(verbose: bool = True) -> None:
    # Get time formatted as a string
    mission_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Prepare arguments for photographer
    detection_args = ["dummy",
                      "--max_time", 3600,  # time [seconds]
                      "--output", f"~/mission_{mission_time}",  #
                      "--mission", "true",  #
                      "--verbose", f"{verbose}"  #
                      ]

    # Call to main photographer detector
    detected = photographer.main(detection_args)

    # Check return flag
    if detected == 1:
        tools.print_msg("Aruco marker detected!, Actioning trapdoor...", verbose=verbose)

        # Action trapdoor
        raspi_servo_simple.main(verbose=verbose)


async def print_status_text(drone, verbose: bool):
    try:
        async for status_text in drone.telemetry.status_text():
            tools.print_msg(f"Status: {status_text.type}: {status_text.text}", verbose=verbose)
    except asyncio.CancelledError:
        return


if __name__ == '__main__':
    # Call main running function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(True))
