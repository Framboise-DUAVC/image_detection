import time
import picamera
import os
import sys
import tools


def usage():
    return "photographer.py --time <int> --freq <int> --output <string:OPTIONAL> --verbose <True/False:OPTIONAL>" \
           "\nAs an Example, 10 seconds operation for 2 pictures/second (frequency) to be dumped in: " \
           "/home/pi/photos_example" \
           "\n\t-> photographer.py --time 10 --freq 2 --output /home/pi/photos_example"


def print_msg(msg, verbose):
    if verbose:
        print(msg)


def safety_check_args(args_dict):
    # Safety check mandatory arguments
    mandatory_list = ["time", "freq"]

    for arg_mandatory in mandatory_list:
        if arg_mandatory not in args_dict:
            print_msg(f"Argument --{arg_mandatory} is mandatory! Please provide it.", verbose=True)
            usage()
            exit(-1)


def main(args):
    # Safety check
    if len(args) == 0:
        print(f"ERROR: No arguments passed!")
        print(usage())
        exit(-1)

    args = sys.argv[1:]

    # Print collected arguments
    print(f"Arguments read: {args}")

    # Set the arguments
    args_dict = tools.parse_arguments(args=args)

    # Set verbosity
    verbose = args_dict["verbose"].lower() == "true" if "verbose" in args_dict else False

    # Check arguments
    safety_check_args(args_dict)

    # Set the arguments
    time_secs = args_dict["time"]
    freq_phot = args_dict["freq"]
    output = args_dict["output"] if "output" in args_dict else "/home/pi/captures/"

    # Compute total iterations
    it_max = int(freq_phot * time_secs) - 1
    time_wait = 1.0 / freq_phot

    if not os.path.exists(output):
        os.mkdir(output)
        if verbose:
            print(f"Successfully created output directory: {output}")

    with picamera.PiCamera() as camera:
        camera.start_preview()
        try:
            for i, filename in enumerate(camera.capture_continuous(os.path.join(output, 'image_{counter:02d}.jpg'))):
                print(filename, verbose)
                time.sleep(time_wait)
                if i == it_max:
                    break
        finally:
            camera.stop_preview()

    print_msg("All done!", verbose)


if __name__ == '__main__':
    # Call main running function
    main(sys.argv[1:] if len(sys.argv[1:]) > 1 else [])
