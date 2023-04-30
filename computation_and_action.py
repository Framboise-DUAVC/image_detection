import math

import mavsdk
import on_y_va
from multiprocessing import Process
import Logger
import datetime
import asyncio
import shapely

import raspi_servo_simple


async def get_gps_coords(drone: mavsdk.System) -> dict:
    async for pos in drone.telemetry.position():
        result = {"lat": pos.latitude_deg,
                  "lon": pos.longitude_deg}

        return result


async def main():

    # Compute current time
    mission_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    mission_fpath = f"/home/pi/mission_gps_{mission_time}"

    # Set logger
    logger = Logger.Logger(logger_filepath=f"{mission_fpath}", verbose=True, dump=True)

    # Connect to the drone
    drone = mavsdk.System()

    # Show info
    logger.print_msg("Trying to connect...")

    # Drone is in serial0
    await drone.connect(system_address="serial:///dev/serial0:921600")

    # Ensure we have future package
    asyncio.ensure_future(print_status_text(drone, logger=logger))

    # Info...
    logger.print_msg("Waiting for drone to connect...")

    # Detection and action test
    output = on_y_va.detection_and_action(restart_photo=False, actuate=False, verbose=True)

    # Constant #########################################################################################################
    aruco_coord = {"lat":45.43960862871248, "lon": -0.4283431162652947}

    # Create a circumference within this point
    alfa_rad = math.atan(20 / (6.371*10**6))

    # Create shapely circumference
    circ_center =shapely.Point(aruco_coord["lat"], aruco_coord["lon"])
    circ = circ_center.buffer(alfa_rad)
    # Constant #########################################################################################################

    # pos = asyncio.ensure_future(get_gps_coords(drone))

    # Launch filmer separately
    filmer = Process(on_y_va.detection_and_action(False, False, True, output, False))
    filmer.start()
    filmer.join()

    # Now, loop entirely
    while True:
        current_coord = await get_gps_coords(drone)

        # Create shapely circumference
        p_gps = shapely.Point(current_coord["lat"], current_coord["lon"])

        # Print them
        logger.print_msg(f"Current GPS location: (lat, lon) [deg]: ({p_gps.x}, {p_gps.y}).")

        # Compute the distance and the heading
        if circ.contains(p_gps):
            logger.print_msg(f"GPS point (lat, lon) [deg]: ({p_gps.x}, {p_gps.y}) is within the radius of the "
                             f"circle (lat, lon) [deg]: ({circ.x}, {circ.y}")

            # Entered to the drop payload radius
            raspi_servo_simple.main(logger=logger)

            # Break
            break
        else:
            logger.print_msg(f"Not in the circle...!")


async def print_status_text(drone, logger: Logger.Logger):
    try:
        async for status_text in drone.telemetry.status_text():
            logger.print_msg(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


if __name__ == '__main__':

    # Call to main running function
    # Call main running function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())