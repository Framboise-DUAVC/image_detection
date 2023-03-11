import time
import picamera
import os
import sys


def usage():
    return "photographer.py <int:time in seconds> <int:frequency> <string:output_directory>[OPTIONAL]" \
           "\nAs an Example, 10 seconds operation for 2 pictures/second (frequency) to be dumped in: " \
           "/home/pi/photos_example" \
           "\n\t-> photographer.py 10 2 /home/pi/photos_example"

def print_msg(msg, verbose):
    if verbose:
        print(msg)

def main(args, verbose=True):
    # Safety check
    if len(args) == 0:
        print(f"ERROR: No arguments passed!")
        print(usage())
        exit(-1)

    args = sys.argv[1:]

    # Print collected arguments
    print(f"Arguments read: {args}")

    # Set the arguments
    time_secs = int(args[0])
    freq_phot = int(args[1])
    output = args[2] if len(args) >= 3 else "/home/pi/captures/"

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

if __name__ == '__main__':

    # Call main running function
    main(sys.argv[1:] if len(sys.argv[1:]) > 1 else [], verbose=False)

    print("All done!", verbose)
