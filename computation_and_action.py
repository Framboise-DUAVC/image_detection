import math

import mavsdk
import on_y_va
from multiprocessing import Process
import Logger
import datetime
import asyncio
import shapely

import raspi_servo_simple


async def get_gps_coords(drone: mavsdk.System, logger: Logger.Logger) -> None:
    async for gps_info in drone.telemetry.gps_info():
        logger.print_msg(f"GPS info: {gps_info}")

    return {"lat": gps_info.lat, "lon": gps_info.lon}


def gps_and_action(drone: mavsdk.System, logger: Logger.Logger):
    # Constant
    aruco_coord = {"lat":45.43960862871248, "lon": -0.4283431162652947}

    # Create a circumference within this point
    alfa_rad = math.atan(20 / (6.371*10**6))

    # Create shapely circumference
    circ_center =shapely.Point(aruco_coord["lat"], aruco_coord["lon"])
    circ = circ_center.buffer(alfa_rad)

    # Current coordinates
    current_coord = {"lat": 45.43936665174612, "lon": -0.42839921605266745}

    # Get the GPS coords and compute the distance
    while True:
        # Get the current latitude and longitude
        current_coord = get_gps_coords(drone=drone, logger=logger)

        # Create shapely object
        p_gps = shapely.Point(current_coord["lat"], current_coord["lon"])

        # Compute the distance and the heading
        if circ.contains(p_gps):
            logger.print_msg(f"GPS point (lat, lon) [deg]: ({p_gps.x}, {p_gps.y}) is within the radius of the circle "
                             f"(lat, lon) [deg]: ({circ.x}, {circ.y}")

            # Entered to the drop payload radius
            raspi_servo_simple.main()

            # Break
            break

def launch_parallel(*fns, args):
    proc = []
    for fn in fns:
        p = Process(target=fn(*args))
        p.start()
        proc.append(p)
    for p in proc:
        p.join()

def main():

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

    # Now, start monitoring gps --> Parallel pipe
    gps_monitor_and_action_args = (drone, logger)
    gps_monitor_and_action = gps_and_action

    # Now, keep doing photos like hell --> Parallel pipe --> DETECTION DISABLED
    filmer_args = (False, False, True, output, False)
    filmer = on_y_va.detection_and_action

    # Launch them parallely: prepare input
    args = [gps_monitor_and_action_args, filmer_args]
    fns = [gps_monitor_and_action, filmer]

    # Launch prallel
    launch_parallel(fns, args)



async def print_status_text(drone, logger: Logger.Logger):
    try:
        async for status_text in drone.telemetry.status_text():
            logger.print_msg(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


if __name__ == '__main__':

    # Call to main running function
    main()