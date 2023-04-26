import asyncio
import mavsdk

import Logger
import banners
import datetime

import photographer
import tools
import raspi_servo_simple


async def main(verbose: bool = True):
    # Get drone object and then try to connect
    drone = mavsdk.System()

    # Show info
    tools.simple_print_msg("Trying to connect...", verbose=verbose)

    # Drone is in serial0
    await drone.connect(system_address="serial:///dev/serial0:921600")

    # Ensure we have future package
    status_text_task = asyncio.ensure_future(print_status_text(drone, verbose=verbose))

    # Info...
    tools.simple_print_msg("Waiting for drone to connect...", verbose=verbose)

    # Get connection state
    async for state in drone.core.connection_state():
        if state.is_connected:
            # Info if connected
            tools.simple_print_msg(f"-- Connected to drone!", verbose=verbose)

            # Show banner
            tools.simple_print_msg(f"{banners.get_px4_banner()}", verbose=verbose)

            # Exit async
            break

    # Info...
    tools.simple_print_msg("-- Arming", verbose=verbose)
    tools.simple_print_msg("test for mav", verbose=verbose)
    # Arm
    #await drone.action.arm()

    # Get the flight mode
    #async for flight_mode in drone.telemetry.flight_mode():
        # Display flight mode
     #   tools.simple_print_msg(f"-- FlightMode: {str(flight_mode)}", verbose=verbose)

    # Status check
    #status_text_task.cancel()


async def print_status_text(drone, verbose: bool):
    try:
        async for status_text in drone.telemetry.status_text():
            tools.simple_print_msg(f"Status: {status_text.type}: {status_text.text}", verbose=verbose)
    except asyncio.CancelledError:
        return


if __name__ == '__main__':
    # Call main running function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(True))
