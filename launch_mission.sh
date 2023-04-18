MAX_TIME="3600"
RECEIVER="bryan@msipre.local"
MISSION="true"
bash embed_launch.sh -o "$HOME/camera_test" -r "${RECEIVER}" -mt "${MAX_TIME}" --mission "${MISSION}" -rm