
# Screen username
uname="bryan"
mission_log="/home/pi/mission_log_${uname}"


# Open screen session
screen -S "${uname}"

# Launch python command
python3 detection_action_test.py | tee "${mission_log}"