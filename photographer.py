import csv
import time
import datetime
from picamera.array import PiRGBArray
import picamera
import os
import sys

import Logger
import tools
import signal

# Project libraries
import PhotoInfo
import photo_analyzer

# Global variable: Signal Entry (Sentry) <-- If someone Ctrl+C --> Sentry == False
Sentry = False


def usage():
    return "---Usage Follows---" \
           "\nphotographer.py --time <int> --freq <int> --output <string:OPTIONAL> --verbose <True/False:OPTIONAL>" \
           "\nAs an Example, 10 seconds operation for 2 pictures/second (frequency) to be dumped in: " \
           "/home/pi/photos_example" \
           "\n\t-> photographer.py --time 10 --freq 2 --output /home/pi/photos_example" \
           "\n"


def safety_check_args(args_dict: dict, logger: Logger.Logger):
    # Safety check mandatory arguments
    mandatory_names = [("max_time", int), ("mission", str)]

    for arg_mandatory in mandatory_names:
        if arg_mandatory[0] not in args_dict:
            logger.print_msg(f"Argument --{arg_mandatory[0]} is mandatory! Please provide it.")
            usage()
            exit(-1)
        else:
            try:
                trial = arg_mandatory[1](args_dict[arg_mandatory[0]])
            except Exception as e:
                logger.print_msg(f"Argument --{arg_mandatory[0]} could not be parsed. Please follow the format.")
                logger.print_msg("---Error Follows---")
                logger.print_msg(f"{e.__str__()}")
                usage()
                exit(-1)


def worker_photo_analyzer(proc_num, frame, filename, id_wanted, logger: Logger, show=False, output=None) -> dict:
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
    logger.print_msg(f"{proc_num} | {filename} | {has_marker} | {'{:.5f}'.format(elapsed)}")

    # Insert to the queue
    return result_dict


def photographer_launcher(args: [], logger: Logger.Logger) -> dict:
    # Safety check
    if len(args) == 0:
        print(f"ERROR: No arguments passed!")
        print(f"{usage()}")
        exit(-1)

    def SignalHandler_SIGINT(SignalNumber, Frame):
        print(f"")
        print(f"Keyboard interruption detected!")
        global Sentry
        Sentry = True


    # Set what function to use in case of Ctr+C event
    signal.signal(signal.SIGINT, SignalHandler_SIGINT)

    # Set the arguments
    args_dict = tools.parse_arguments(args=args)

    # Set verbosity
    verbose = args_dict["verbose"].lower() == "true" if "verbose" in args_dict else False

    # Ensure arguments
    safety_check_args(args_dict, logger)

    # Set the arguments
    max_time = int(args_dict["max_time"])
    output = args_dict["output"] if "output" in args_dict else "/home/pi/captures/"
    show = args_dict["show"] if "show" in args_dict else False
    mission = True if args_dict["mission"].lower() == "true" else False
    offset = int(args_dict["offset"]) if "offset" in args_dict else 0
    output = os.path.abspath(output)

    # Set the logger options
    logger.update_verbosity(verbosity=verbose)
    logger.update_logpath(logger_filepath=os.path.join(output, "python_logger.log"))

    # Do break? OPTIONAL ARGUMENTS
    do_break = True
    if "do_break" in args_dict:
        do_break = False if args_dict["do_break"].lower() == "false" else True

    # Compute total iterations
    if not os.path.exists(output):
        # Create absolute path
        os.mkdir(output)
        logger.print_msg(f"Successfully created output directory: {output}")
    else:
        logger.print_msg(f"Directory previously existing, not overriding: {output}")

    # Append here the processes
    jobs_return_dict = {}

    # Print info
    if offset == 0:
        logger.print_msg(f"Proc. num. | Filename | Marker detected | Elapsed time")

    # Here we can either call CAPTURE_CONTINUOUS or TBD: CAPTURE_VIDEO
    detection_dict_flags = continuous_capture(jobs_return_dict, output, show, max_time,
                                              logger=logger,
                                              mission=mission,
                                              do_break=do_break,
                                              offset=offset)

    # Print csv file in output folder
    summary_path = os.path.join(output, "summary.csv")
    summary_exists = os.path.exists(summary_path)

    # Info
    if summary_exists:
        logger.print_msg(f"Summary file already exists!, Appending data to it... File: {summary_path}")

    with open(summary_path, "a" if summary_exists else "w") as fcsv:
        csvwriter = csv.writer(fcsv)

        if not summary_exists:
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
        if detection_dict_flags["detected"] and not detection_dict_flags["interrupt"]:
            return detection_dict_flags
        elif detection_dict_flags["detected"] and detection_dict_flags["interrupt"]:
            logger.print_msg(f"Aruco was detected but keyboard interruption!")
        else:
            logger.print_msg(f"Aruco couldn't be detected after '{max_time}' seconds.")

        # Info
        logger.print_msg(f"Exiting function and returning empty dictionary...")

    # If it is not mission mode, then convert numpy to jpg
    tools.convert_numpy_to_jpg(output, logger=logger)

    # Info
    logger.print_msg("All done!")

    # Return
    return {}


def continuous_capture(result_dict, output, show, max_time, logger, mission=False, do_break=True,
                       offset=0) -> dict:
    # Set counter
    i = offset

    # Shutter indexes for testing
    shutt_idx = 1

    # Set the array
    shutters_array = range(100, 30000, 1000)

    # Aruco detected?
    aruco_detected = False
    aruco_photo_id = -1
    signal_interrupt = False

    # Start time counter
    start_time = datetime.datetime.now()

    logger.print_msg("Starting continuous capture...")
    with picamera.PiCamera() as camera:
        camera.start_preview()
        # camera.resolution = (640, 480)
        logger.print_msg(f"Current framerate: {camera.framerate}")
        logger.print_msg(f"Current shutter_speed: {camera.shutter_speed}")
        logger.print_msg(f"Current exposure speed: {camera.exposure_speed}")
        camera.framerate = 24
        camera.shutter_speed = 150  # 150 ... to .... 9000000
        logger.print_msg(f"Set framerate: {camera.framerate}")
        logger.print_msg(f"Set shutter_speed: {camera.shutter_speed}")

        # Check exposure speed
        logger.print_msg(f"Current exposure speed: {camera.exposure_speed}")

        rawCapture = PiRGBArray(camera, size=(camera.resolution[0], camera.resolution[1]))
        try:
            # capture frames from the camera
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # grab the raw NumPy array representing the image, then initialize the timestamp
                # and occupied/unoccupied text
                image = frame.array

                filename = os.path.join(output, f"raspy_exp_id_{str(i).zfill(10)}_exp_{camera.shutter_speed}.npy")

                # Build arguments
                job1_args = (i, image, filename, 7, logger, show, filename.replace('.jpg', '-Analyzed.jpg'))

                # Launch process to evaluate image
                result_dict[i] = worker_photo_analyzer(*job1_args)

                # If mission mode
                if mission:
                    has_marker = result_dict[i]["info"].get_has_marker()

                    if has_marker:

                        # Build message to display
                        msg2print = f"Aruco marker detected in iteration number; '{i}'. "

                        if do_break:
                            msg2print += f"Exiting photographer loop!"
                        else:
                            msg2print += f"Keeping in photographer loop..."

                        logger.print_msg(f"{msg2print}")

                        # Set aruco detected to True
                        aruco_detected = True
                        aruco_photo_id = i

                        # If not "do_break", don't break the loop
                        if do_break:
                            break

                # Check timing process_time = final_time - initial_time
                current_time = datetime.datetime.now()
                elapsed_time = current_time - start_time

                # Time to sleep
                if elapsed_time.total_seconds() > max_time:
                    break

                rawCapture.truncate(0)
                i += 1

                # In case of Ctr+C, brake the loop
                if Sentry:
                    logger.print_msg(f"Safely getting out of the main loop!")
                    signal_interrupt = True
                    break

                # Modify the shutter speed
                camera.shutter_speed = shutters_array[shutt_idx]

                # Go next value
                if i % 20 == 0:
                    shutt_idx += 1

                # Check overshoot
                if shutt_idx > len(shutters_array) - 1:
                    shutt_idx = 0

        finally:
            camera.stop_preview()

    # Result dictionary
    result = {
        "detected": aruco_detected,
        "id": aruco_photo_id,
        "interrupt": signal_interrupt
    }

    # Return boolean
    return result


def main():
    # Set fast logger
    logger = Logger.Logger(logger_filepath=None, verbose=True, dump=False)

    # Call main running function
    photographer_launcher(sys.argv[1:] if len(sys.argv[1:]) > 1 else [], logger=logger)


if __name__ == '__main__':
    # Call main running function
    main()
