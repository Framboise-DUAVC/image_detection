import sys
import tools
import Logger


def main():
    # Set fast logger
    logger = Logger.Logger(logger_filepath=None, verbose=True, dump=False)

    # Convert photos
    tools.convert_numpy_to_jpg(sys.argv[1], logger)


if __name__ == '__main__':
    # Call to main running function
    main()
