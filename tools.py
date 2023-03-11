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
