import asyncio
import mavsdk
import photographer


async def main():
    # ser = serial.Serial('/dev/ttyFAKE0')  # open serial port
    drone = mavsdk.System()
    print("Trying to connect...")
    await drone.connect(system_address="udp://:14540")
    status_text_task = asyncio.ensure_future(print_status_text(drone))
    print("Waiting for drone to connect...")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    async for flight_mode in drone.telemetry.flight_mode():
        print("FlightMode:", str(flight_mode))
        if str(flight_mode) == 'MANUAL':
            print("YEEEE HAWWWW")
            print("I feel the need...the need for speed!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    print("-- Waiting for cruise altitude...")
    async for flight_mode in drone.telemetry.flight_mode():
        print("FlightMode:", str(flight_mode))
        if str(flight_mode) == 'CRUISE':
            print("-- Starting photographer...")
            break

    print("-- Landing")
    await drone.action.land()

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
