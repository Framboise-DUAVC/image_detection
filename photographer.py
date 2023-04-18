import csv
import glob
import time
import datetime
from picamera.array import PiRGBArray
import picamera
import os
import sys
import tools
import numpy as np
import cv2

# Project libraries
import PhotoInfo
import photo_analyzer


def usage():
    return "---Usage Follows---" \
           "\nphotographer.py --time <int> --freq <int> --output <string:OPTIONAL> --verbose <True/False:OPTIONAL>" \
           "\nAs an Example, 10 seconds operation for 2 pictures/second (frequency) to be dumped in: " \
           "/home/pi/photos_example" \
           "\n\t-> photographer.py --time 10 --freq 2 --output /home/pi/photos_example" \
           "\n"


def safety_check_args(args_dict):
    # Safety check mandatory arguments
    mandatory_names = [("max_time", int), ("mission", str)]

    for arg_mandatory in mandatory_names:
        if arg_mandatory[0] not in args_dict:
            tools.print_msg(f"Argument --{arg_mandatory} is mandatory! Please provide it.", verbose=True)
            usage()
            exit(-1)
        else:
            try:
                trial = int(args_dict[arg_mandatory[0]])
            except Exception as e:
                tools.print_msg(f"Argument --{arg_mandatory[0]} could not be parsed. Please follow the format.", verbose=True)
                tools.print_msg("---Error Follows---", verbose=True)
                tools.print_msg(f"{e.__str__()}", verbose=True)
                usage()
                exit(-1)


def worker_photo_analyzer(proc_num, frame, filename, id_wanted, show=False, output=None, verbose=True) -> dict:
    # Start time
    start = time.time()

    # Set as an empty dictionary
    result_dict = {}

    # Call function
    has_marker = photo_analyzer.photo_analyzer(frame=frame, filename=filename, id_wanted=id_wanted, show=show,
                                               output=output)

    # End time
    elapsed = time.time() - start

    # Save stuff
    result_dict["info"] = PhotoInfo.PhotoInfo(filename=filename, has_marker=has_marker)
    result_dict["time"] = elapsed
    result_dict["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print info
    tools.print_msg(f"{proc_num} | {filename} | {has_marker} | {elapsed}", verbose)

    # Insert to the queue
    return result_dict


def worker_check_triggers(jobs_return_dict_last_obj, threshold, escape, verbose):
    # Counter of triggers
    counter = 0

    if not escape:
        has_marker = jobs_return_dict_last_obj.get_has_marker()

        if has_marker:
            counter += 1

        if counter >= threshold:
            if verbose:
                tools.print_msg(f"Marker detected '{counter}' times!", verbose)
            escape = True


def main(args):
    # Safety check
    if len(args) == 0:
        print(f"ERROR: No arguments passed!")
        print(usage())
        exit(-1)

    # Get the useful arguments
    args = sys.argv[1:]

    # Set the arguments
    args_dict = tools.parse_arguments(args=args)

    # Set verbosity
    verbose = args_dict["verbose"].lower() == "true" if "verbose" in args_dict else False

    # Ensure arguments
    safety_check_args(args_dict)
    
    # Set the arguments
    max_time = int(args_dict["max_time"])
    output = args_dict["output"] if "output" in args_dict else "/home/pi/captures/"
    show = args_dict["show"] if "show" in args_dict else False
    mission = True if args_dict["mission"].lower() == "true" else False

    # Compute total iterations
    if not os.path.exists(output):
        os.mkdir(output)
        tools.print_msg(f"Successfully created output directory: {output}", verbose)

    # Append here the processes
    jobs_return_dict = {}

    # Print info
    tools.print_msg(f"Proc. num. | Filename | Marker detected | Elapsed time", verbose)

    # Here we can either call CAPTURE_CONTINUOUS or TBD: CAPTURE_VIDEO
    continuous_capture(jobs_return_dict, output, show, max_time, verbose, mission=mission)
    
    # Print csv file in output folder
    with open(os.path.join(output, "summary.csv"), "w") as fcsv:
        csvwriter = csv.writer(fcsv)

        csvwriter.writerow(["Process number", "Filename", "Marker detected", "Elapsed time", "Date"])

        for job_id in jobs_return_dict:
            proc_filename = jobs_return_dict[job_id]["info"].get_filename()
            has_marker = jobs_return_dict[job_id]["info"].get_has_marker()
            elapsed_time = jobs_return_dict[job_id]["time"]
            date_time = jobs_return_dict[job_id]["date"]
            row2write = [job_id, proc_filename, has_marker, elapsed_time, date_time]
            csvwriter.writerow(row2write)

    # If mission mode, exit rapidly and return flag==1
    if mission:
        exit(1)

    # If it is not mission mode, then convert numpy to jpg
    tools.convert_numpy_to_jpg(output, verbose=verbose)

    # Info
    tools.print_msg("All done!", verbose=verbose)


def continuous_capture(result_dict, output, show, max_time, verbose=True, mission=False):
    # Set counter
    i = 0

    # Start time counter
    start_time = datetime.datetime.now()

    tools.print_msg("Starting continuous capture...", verbose)
    with picamera.PiCamera() as camera:
        camera.start_preview()
        # camera.resolution = (640, 480)
        # camera.framerate = 32
        rawCapture = PiRGBArray(camera, size=(camera.resolution[0], camera.resolution[1]))
        try:
            # capture frames from the camera
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # grab the raw NumPy array representing the image, then initialize the timestamp
                # and occupied/unoccupied text
                image = frame.array

                filename = os.path.join(output, f"raspy_{str(i).zfill(10)}.npy")

                # Build arguments
                job1_args = (i, image, filename, 7, show, filename.replace('.jpg', '-Analyzed.jpg'), verbose)

                # Launch process to evaluate image
                result_dict[i] = worker_photo_analyzer(*job1_args)

                # If mission mode
                if mission:
                    has_marker = result_dict[i]["info"].get_has_marker()
                    
                    if has_marker:
                        tools.print_msg(f"Aruco marker detected in iteration number; '{i}'. Exiting photographer loop!",
                                  verbose=verbose)
                        break

                # Ellapsed time for processing
                elapsed = result_dict[i]["time"]

                # Check timing process_time = final_time - initial_time
                current_time = datetime.datetime.now()
                elapsed_time = current_time - start_time

                # Time to sleep
                if elapsed_time.total_seconds() > max_time:
                    break

                rawCapture.truncate(0)

                i += 1

        finally:
            camera.stop_preview()


if __name__ == '__main__':
    # Call main running function
    main(sys.argv[1:] if len(sys.argv[1:]) > 1 else [])
