from pymavlink import mavutil
vehicle = mavutil.mavlink_connection('tcpin:localhost:4560')
vehicle.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (vehicle.target_system, vehicle.target_component))