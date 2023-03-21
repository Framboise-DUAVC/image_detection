import asyncio
import mavsdk
import serial

async def main():
    # ser = serial.Serial('/dev/ttyFAKE0')  # open serial port
    drone = mavsdk.System()
    print("Trying to connect...")
    await drone.connect(system_address="tcp:///dev/ttyFAKE0:115200")
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


if __name__ == '__main__':
    # Call main running function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())