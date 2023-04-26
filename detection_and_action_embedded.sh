# Screen username
mission_name="detection_action-$1"
mission_log="/home/pi/mission_log_${mission_name}.log"

# Launch python command
python3 detection_action_test.py | tee "${mission_log}"