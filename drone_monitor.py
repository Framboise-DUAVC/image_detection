#!/usr/bin/env python3

import asyncio
from mavsdk import System


async def run():
    # Init the drone
    drone = System()
    print("Trying to connect...")
    await drone.connect(system_address="serial:///dev/serial0:921600")

    print("Connected to the drone!")
    # await drone.connect(system_address="udp://:14540")
    # Start the tasks
    # pos = asyncio.ensure_future(print_position(drone))

    while True:
        pos = await print_position(drone)
        print(pos)


async def print_battery(drone):
    async for battery in drone.telemetry.battery():
        print(f"Battery: {battery.remaining_percent}")


async def print_gps_info(drone):
    async for gps_info in drone.telemetry.gps_info():
        print(f"GPS info: {gps_info}")


async def print_in_air(drone):
    async for in_air in drone.telemetry.in_air():
        print(f"In air: {in_air}")


async def print_position(drone):
    async for position in drone.telemetry.position():

        result = {"lat": position.latitude_deg,
                  "lon": position.longitude_deg}

        return result


if __name__ == "__main__":
    # Start the main function
    asyncio.run(run())