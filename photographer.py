import csv
import multiprocessing
import time
import datetime
import picamera
import os
import sys
import tools

# Project libraries
import PhotoInfo
import photo_analyzer


def print_msg(msg, verbose):
    if verbose:
        print(msg)


def usage():
    return "---Usage Follows---" \
           "\nphotographer.py --time <int> --freq <int> --output <string:OPTIONAL> --verbose <True/False:OPTIONAL>" \
           "\nAs an Example, 10 seconds operation for 2 pictures/second (frequency) to be dumped in: " \
           "/home/pi/photos_example" \
           "\n\t-> photographer.py --time 10 --freq 2 --output /home/pi/photos_example" \
           "\n"


def safety_check_args(args_dict):
    # Safety check mandatory arguments
    mandatory_names = [("time", int), ("freq", int)]

    for arg_mandatory in mandatory_names:
        if arg_mandatory[0] not in args_dict:
            print_msg(f"Argument --{arg_mandatory} is mandatory! Please provide it.", verbose=True)
            usage()
            exit(-1)
        else:
            try:
                trial = int(args_dict[arg_mandatory[0]])
            except Exception as e:
                print_msg(f"Argument --{arg_mandatory[0]} could not be parsed. Please follow the format.", verbose=True)
                print_msg("---Error Follows---", verbose=True)
                print_msg(f"{e.__str__()}", verbose=True)
                usage()
                exit(-1)


def worker_photo_analyzer(proc_num, filename, id_wanted, show=False, output=None, verbose=True) -> dict:
    # Start time
    start = time.time()

    # Set as an empty dictionary
    result_dict = {}

    # Call function
    has_marker = photo_analyzer.photo_analyzer(filename=filename, id_wanted=id_wanted, show=show, output=output)

    # End time
    elapsed = time.time() - start

    # Save stuff
    result_dict["info"] = PhotoInfo.PhotoInfo(filename=filename, has_marker=has_marker)
    result_dict["time"] = elapsed
    result_dict["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print info
    print_msg(f"{proc_num} | {filename} | {has_marker} | {elapsed}", verbose)

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
                print_msg(f"Marker detected '{counter}' times!", verbose)
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

    # Check arguments
    safety_check_args(args_dict)

    # Set the arguments
    time_secs = int(args_dict["time"])
    freq_phot = int(args_dict["freq"])
    output = args_dict["output"] if "output" in args_dict else "/home/pi/captures/"
    show = args_dict["show"] if "show" in args_dict else False

    # Compute total iterations
    it_max = int(freq_phot * time_secs) - 1
    time_wait = 1.0 / freq_phot

    if not os.path.exists(output):
        os.mkdir(output)
        if verbose:
            print_msg(f"Successfully created output directory: {output}", verbose)

    # Multiprocesser manager
    return_queue = multiprocessing.Queue()

    # Append here the processes
    jobs_return_dict = {}

    # Print info
    print_msg(f"Proc. num. | Filename | Marker detected | Elapsed time", verbose)

    with picamera.PiCamera() as camera:
        camera.start_preview()
        try:
            for i, filename in enumerate(camera.capture_continuous(os.path.join(output, 'image_{counter:02d}.jpg'))):
                # Build arguments
                job1_args = (i, filename, 7, return_queue, show, filename.replace('.jpg', '-Analyzed.jpg'), verbose)

                # Launch process to evaluate image
                jobs_return_dict[i] = worker_photo_analyzer(*job1_args)

                # Append job
                # jobs.append(p1)

                # Start job
                # p1.start()

                # Every 5 photos check if we are done
                # job2_args = (jobs_return_dict[i], 5, escape, verbose)
                # p2 = Process(target=worker_check_triggers, args=job2_args)
                # p2.start()

                # if escape:
                #     print_msg("Marker detected! Exiting the loop!", verbose)
                #     break

                # Time to sleep
                time.sleep(time_wait)

                # Finish loop
                if i == it_max:
                    break
        finally:
            camera.stop_preview()

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

    print_msg("All done!", verbose)


if __name__ == '__main__':
    # Call main running function
    main(sys.argv[1:] if len(sys.argv[1:]) > 1 else [])
