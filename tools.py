import os
import numpy as np
import cv2

def parse_arguments(args, verbose=False):
    """
    Parse arguments, given a list.
    Reminder: Arguments should be this format: --<key_word> <value>
    :param args: given arguments
    :param verbose: verbosity boolean
    :return: dictionary with arguments
    """

    # Create empty dictionary
    parsed_dict = {}

    # Iterate through the list of arguments and their values
    for i, arg in enumerate(args):
        if "--" in arg:
            key = arg.replace("--", "")
            parsed_dict[key] = ""

            # Then, we should add the value
            # Safety check if it exists
            if i + 1 > len(args) - 1:
                if verbose:
                    print(f"Error when parsing argument '{arg}', no value found.")
                exit(-1)
            else:
                # Assign value
                parsed_dict[key] = args[i + 1]
                continue
        else:
            continue

    # Return successful
    return parsed_dict


def convert_numpy_to_jpg(dirpath: os.PathLike or str, verbose: bool) -> None:
    # Get objects in the folder
    np_files = os.listdir(dirpath)

    # Info
    print_msg("Converting numpy files to jpg files...", verbose=verbose)

    # Convert files
    for np_file in np_files:
        if np_file.endswith(".npy"):
            # Build filepath
            np_filepath = os.path.join(dirpath, np_file)

            with open(np_filepath, 'rb') as f:
                np_frame = np.load(f)
                cv2.imwrite(np_filepath.replace(".npy", ".jpg"), np_frame)

            # Get rid of the numpy file
            os.remove(np_filepath)

    # Info
    print_msg("All files converted!", verbose=verbose)


def print_msg(msg: str, verbose: bool):
    if verbose:
        print(msg)
