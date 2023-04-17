#!/bin/bash

# Usage
usage="bash embed_launch.sh --output <filename> --receiver"


# Positional arguments
POSITIONAL_ARGS=()

# Preset some arguments
rm_after=0

# Iterate through the arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -o|--output)
      OUTPUT="$2"
      shift # past argument
      shift # past value
      ;;
    -r|--receiver)
      RECEIVER="$2"
      shift # past argument
      shift # past value
      ;;
    -mt|--max_time)
      FREQ_ARG="$2"
      shift # past argument
      shift # past value
      ;;
    -rm|--remove)
          rm_after=1
          shift # past argument
          shift # past value
          ;;
    --default)
      DEFAULT=YES
      shift # past argument
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

# Set the arguments for the python call
PYTHON_SCRIPT="photographer.py"
TIME=20
FREQ=5
if ! [ -z "$FREQ_ARG" ]
then
  FREQ="$FREQ_ARG"
fi
VERBOSE=True

echo "PYTHON_SCRIPT   = ${PYTHON_SCRIPT}"
echo "OUTPUT          = ${OUTPUT}"
echo "TIME            = ${TIME}"
echo "VERBOSE         = ${VERBOSE}"
if [ -z "$RECEIVER" ]
then
  echo "NOT SENDING RESULTS."
else
  echo "SENDING TO..    = ${RECEIVER}"
fi

# Call python file
if [ -z "$OUTPUT" ]
then
      printf "Usage: \n%s\n" "$usage"
else
      echo "Launching script..."
      python3 "${PYTHON_SCRIPT}" --time "${TIME}" --max_time "${FREQ}" --output "${OUTPUT}" --verbose "${VERBOSE}"
fi

# Get the output name for the tar
OUTPUT_TAR="$OUTPUT".tar.gz

# Tar the file
tar czvf "$OUTPUT_TAR" "$OUTPUT"

# Send it to
if ! [ -z "$RECEIVER" ]
then
  echo "SENDING TO..    = ${RECEIVER}"
  scp "$OUTPUT_TAR" "$RECEIVER":~/Downloads/
fi

# TODO: Removing the zipped and the created folder only if required
if [ $rm_after -eq 1 ]
then
  echo "Removing output folder: ${OUTPUT}"
  rm -rf "${OUTPUT}"

  echo "Removing output tared file: ${OUTPUT_TAR}"
  rm -rf "${OUTPUT}"
else
  echo "Leaving all the created files!"
fi