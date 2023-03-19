import os

import cv2
import matplotlib.pyplot as plt


def photo_analyzer(filename, id_wanted, show=False, output=None, rotate=None):
    # Local auxiliary variable
    trigger = False

    # Load the image
    frame = cv2.imread(filename)

    # Rotate if desired
    if rotate is not None:
        frame = cv2.rotate(frame, rotate)

    if show:
        cv2.imshow('Original', frame)
        cv2.waitKey(0)

    # Use the cvtColor() function to grayscale the image
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if show:
        cv2.imshow('Grayscale', gray_image)
        cv2.waitKey(0)
        # Window shown waits for any key pressing event
        # Window shown waits for any key pressing event
        # Window shown waits for any key pressing event

        cv2.destroyAllWindows()

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(gray_image)
    frame_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), markerCorners, markerIds)

    if markerIds is not None:
        for id in markerIds:
            if id == id_wanted:
                trigger = True

    if show or output is not None:
        plt.figure(figsize=(16, 9) if (rotate is None) or (rotate == cv2.ROTATE_180) else (9, 16))
        plt.imshow(frame_markers, origin="upper")
        if markerIds is not None:
            for i in range(len(markerIds)):
                c = markerCorners[i][0]
                plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "+", label="id={0}".format(markerIds[i]))
                """for points in rejectedImgPoints:
                    y = points[:, 0]
                    x = points[:, 1]
                    plt.plot(x, y, ".m-", linewidth = 1.)"""
        plt.legend()
        if show:
            plt.show()
        if output is not None:
            plt.savefig(output)

    return trigger


def archive_analyzer(archive, id_wanted, rotate=None):
    # Get all the files within this archive
    filenames = os.listdir(archive)

    # Build output dir
    output_dir = os.path.join(archive, "analyzed")

    # Check if exist
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Get filepaths
    for filename in filenames:

        # Check if it is an image
        if filename.endswith(".jpg"):
            # Join path
            filepath = os.path.join(archive, filename)

            # Get output path
            output = os.path.join(output_dir, filename)

            # Send to analyzer
            photo_analyzer(filepath, id_wanted, output=output, rotate=rotate)


def main(general_path, id_wanted, rotate=None):
    # Check if dir or file
    if os.path.isdir(general_path):
        archive_analyzer(general_path, id_wanted, rotate)
    elif os.path.isfile(general_path):
        photo_analyzer(general_path, id_wanted, True)


# TODO: remove this
if __name__ == '__main__':
    # Some performed tests
    # WARNING: Change this values if you want to analyze them...
    photo_test_huge_aruco_cardboard = "/home/bryan/CLionProjects/ISAE/image_detection/test/out/photo_test_huge_aruco_cardboard"
    photo_test_huge_aruco_outside = "/home/bryan/CLionProjects/ISAE/image_detection/test/out/photo_test_huge_aruco_outside"

    # Call main function
    main(
        general_path=photo_test_huge_aruco_outside,
        id_wanted=7,
        rotate=cv2.ROTATE_90_CLOCKWISE)
