import os


class Logger:
    # Filepath
    __log_dir = None
    __log_filepath = None
    __log_exists = None

    # Actions
    __be_verbose = True
    __do_dumper = True

    # Options
    __append = "a"
    __write = "w"

    # How do we write?
    __how_write = ""

    # Vector containing all the messages
    __archive = []

    def __init__(self, logger_filepath: str or None, verbose: bool = True, dump: bool = True):
        # Set inputs
        self.__log_filepath = logger_filepath
        self.__be_verbose = verbose
        self.__do_dumper = dump

        # Info
        self.print_msg(f"Setting logger verbosity option: {self.__be_verbose}")
        self.print_msg(f"Setting logger dump option: {self.__do_dumper}")

        # Filepath checks
        self.__logpath_safety_checks()

    def __del__(self):
        # Dump messages
        self.__dump()

    def __logpath_safety_checks(self):
        if self.__log_filepath is None:
            self.print_msg(f"Logger file is None!, Skipping checks...")
            return

        # Get directory name
        self.__log_dir = os.path.dirname(self.__log_filepath)

        # Is the filepath existing
        self.__log_exists = os.path.exists(self.__log_filepath)

        # Info
        self.print_msg(f"Setting logger filepath: {self.__log_filepath}")

        # Check if directory exist
        if os.path.exists(self.__log_dir):
            self.print_msg(f"Directory {self.__log_dir} is not created!")
        else:
            self.print_msg(f"Directory {self.__log_dir} is already created!")

        # Check returned flag
        if self.__log_exists:
            self.print_msg(f"Logger file already existing: {self.__log_filepath}")
            self.print_msg(f"When dumping, data will be appended there!")
        else:
            self.print_msg(f"Logger file not existing: {self.__log_filepath}")
            self.print_msg(f"When dumping, this file will be created!")

    def __dump(self):
        # Should we dump?
        if not self.__do_dumper:
            self.print_msg(f"Not dumping in any file...")
            return

        if self.__log_filepath is None:
            self.print_msg(f"Not dumping in any file, logger file is set to None...")
            return

            # Should we append or brand new write?
        self.__how_write = self.__append if self.__log_exists else self.__write

        # Info
        msg2write = "append file" if self.__append else "write file"

        # Info
        self.print_msg(f"File will be wrote: {msg2write}")

        if not os.path.exists(self.__log_dir):
            # Info
            self.print_msg(f"Directory is still not existing, I need to create it to dump the messages.")
            self.print_msg(f"Creating directory...: {self.__log_dir}")

            # Create it
            os.mkdir(self.__log_dir)

            # Info
            self.print_msg(f"Directory created!")

        # Info
        self.print_msg(f"Dumping all logger data... Num. of messages: {len(self.__archive) + 1}")

        # Dump all the stored logs in the file
        with open(self.__log_filepath, self.__how_write) as f:
            f.writelines(self.__archive)

    def __save_msg(self, msg: str):
        # Save the message in the archive
        self.__archive.append(msg + "\n")

    def print_msg(self, msg: str):
        # If verbose mode, display the message
        if self.__be_verbose:
            print(msg)

        # Save the message
        if self.__do_dumper:
            self.__save_msg(msg)

    def update_logpath(self, logger_filepath: str):
        # Update path
        self.__log_filepath = logger_filepath

        # Info
        self.print_msg(f"Updated logger path: {self.__log_filepath}")

        # Filepath checks and subsequent updates
        self.__logpath_safety_checks()

    def update_verbosity(self, verbosity: bool):
        # Update verbosity
        self.__be_verbose = verbosity

        # Info
        self.print_msg(f"Updating logger verbosity option: {self.__be_verbose}")
