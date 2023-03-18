#!/bin/bash

# Usage
usage="bash embed_launch.sh --output <filename>"


# Positional arguments
POSITIONAL_ARGS=()

# Iterate through the arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -o|--output)
      OUTPUT="$2"
      shift # past argument
      shift # past value
      ;;
    -s|--searchpath)
      SEARCHPATH="$2"
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
VERBOSE=True

echo "PYTHON_SCRIPT   = ${PYTHON_SCRIPT}"
echo "OUTPUT          = ${OUTPUT}"
echo "TIME            = ${TIME}"
echo "FREQUENCY       = ${FREQ}"
echo "VERBOSE         = ${VERBOSE}"

# Call python file
if [ -z "$OUTPUT" ]
then
      printf "Usage: \n%s\n" "$usage"
else
      echo "Launching script..."
      python3 "${PYTHON_SCRIPT}" --time "${TIME}" --freq "${FREQ}" --output "${OUTPUT}" --verbose "${VERBOSE}"
fi

# Get the output name for the tar
OUTPUT_TAR="$OUTPUT".tar.gz

# Tar the file
tar czvf "$OUTPUT_TAR" "$OUTPUT"