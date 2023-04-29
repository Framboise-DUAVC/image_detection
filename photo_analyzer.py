import os
import numpy as np
import cv2
import matplotlib.pyplot as plt

good_ones = [7, 97, 216, 222, 62, 184]

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

    # Modify the parameters
    print(f"Default: parameters.adaptiveThresholdConstant: {parameters.adaptiveThreshConstant}")
    print(f"Default: parameters.errorCorrectionRate: {parameters.errorCorrectionRate}")
    print(f"Default: parameters.errorCorrectionRate: {parameters.minMarkerPerimeterRate}")
    # parameters.adaptiveThreshConstant = 4
    parameters.errorCorrectionRate = 2.0

    possible_rates = np.arange(0.03, 0.3, 0.001)

    #for rate in possible_rates:
    #    parameters.minMarkerPerimeterRate = rate
#
    #    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
#
    #    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(gray_image)
    #    frame_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), markerCorners, markerIds)
#
    #    if len(markerIds) == 1:
    #        print(f"Number of markers: {len(markerIds)} - Possible rate: {rate}")
    #        break

    # Optimal value for min marker perimeter rate: 0.06300000000000003
    opt_rate = 0.06200000000000003
    parameters.minMarkerPerimeterRate = opt_rate
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(gray_image)
    frame_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), markerCorners, markerIds)



    if markerIds is not None:
        for id in markerIds:
            if id in good_ones:
                print(f"Aruco detected: {filename}")
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
            plt.cla()
            plt.clf()

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


def test():
    img = cv2.imread(pathinput)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    print("Number of contours detected:", len(contours))

    for cnt in contours:
        x1,y1 = cnt[0][0]
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(cnt)
            ratio = float(w)/h
            if ratio >= 0.9 and ratio <= 1.1:
                img = cv2.drawContours(img, [cnt], -1, (0,255,255), 3)
                cv2.putText(img, 'Square', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            else:
                cv2.putText(img, 'Rectangle', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                img = cv2.drawContours(img, [cnt], -1, (0,255,0), 3)

    cv2.imshow("Shapes", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def test2():
    # Load the image
    img = cv2.imread(pathinput)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply a thresholding operation
    thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]

    # Find the contours in the binary image
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate over the contours and filter out non-box-like contours
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w)/h
        if aspect_ratio > 0.9 and aspect_ratio < 1.1:
            # Draw a rectangle around the contour
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display the image with boxes drawn around the white boxes
    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def test3():
    # Load the image
    img = cv2.imread(pathinput)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply a thresholding operation
    thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]

    # Find the contours in the binary image
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate over the contours and filter out non-box-like contours
    for contour in contours:
        # Get the perimeter of the contour
        perimeter = cv2.arcLength(contour, True)

        # Approximate the contour as a polygon
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

        # Check if the polygon has four sides (i.e., is roughly rectangular)
        if len(approx) == 4:
            # Fit a rotated rectangle around the contour
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            # Compute the aspect ratio of the rectangle
            w, h = rect[1]
            aspect_ratio = float(w) / h if h != 0 else 0

            # Check if the aspect ratio is within a certain range
            if aspect_ratio > 0.9 and aspect_ratio < 1.1:
                # Draw a rectangle around the contour
                cv2.drawContours(img, [box], 0, (0, 255, 0), 2)

    # Display the image with boxes drawn around the white boxes
    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def test4():
    # Load the image
    img = cv2.imread(pathinput)

    # Apply a bilateral filter to reduce noise and preserve edges
    blurred = cv2.bilateralFilter(img, 9, 75, 75)

    # Convert the image to grayscale
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # Apply a thresholding operation
    thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]

    # Find the contours in the binary image
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate over the contours and filter out non-box-like contours
    for contour in contours:
        # Get the perimeter of the contour
        perimeter = cv2.arcLength(contour, True)

        # Approximate the contour as a polygon
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

        # Check if the polygon has four sides (i.e., is roughly rectangular)
        if len(approx) == 4:
            # Fit a rotated rectangle around the contour
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            # Compute the aspect ratio of the rectangle
            w, h = rect[1]
            aspect_ratio = float(w) / h if h != 0 else 0

            # Check if the aspect ratio is within a certain range
            if aspect_ratio > 0.9 and aspect_ratio < 1.1:
                # Draw a rectangle around the contour
                cv2.drawContours(img, [box], 0, (0, 255, 0), 2)

    # Display the image with boxes drawn around the white boxes
    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# TODO: remove this
if __name__ == '__main__':
    # Some performed tests
    # WARNING: Change this values if you want to analyze them...
    photo_test_huge_aruco_cardboard = "/home/bryan/CLionProjects/ISAE/image_detection/test/out/photo_test_huge_aruco_cardboard"
    photo_test_huge_aruco_outside = "/home/bryan/CLionProjects/ISAE/image_detection/test/out/photo_test_huge_aruco_outside"
    photo_test_huge_aruco_MISSION_0 = "/home/bryan/Downloads/testDay1/KshitijTest2/home/pi/mission_20230423_132310/raspy_0000000903.jpg"
    photo_test_huge_aruco_MISSION_1 = "/home/bryan/CLionProjects/ISAE/image_detection/test/out/mission_20230427_170253"
    photo_test_huge_aruco_MISSION_1_photo1 = "/home/bryan/CLionProjects/ISAE/image_detection/test/out/mission_20230427_170253/raspy_exp_id_0000000479_exp_2240.jpg"
    photo_test_huge_aruco_MISSION_1_photo2 = "/home/bryan/CLionProjects/ISAE/image_detection/test/out/mission_20230427_170253/raspy_exp_id_0000000427_exp_2032.jpg"
    photo_test_huge_aruco_MISSION_1_photo2_mod = "/home/bryan/Downloads/mission_20230427_170253/modified/raspy_exp_id_0000000427_exp_2032_mod.jpg"
    photo_test_huge_aruco_MISSION_1_photo2_mod2 = "/home/bryan/Downloads/mission_20230427_170253/modified/raspy_exp_id_0000000427_exp_2032_mod2.jpg"
    photo_test_huge_aruco_MISSION_1_photo2_mod_simu_tape = "/home/bryan/Downloads/mission_20230427_170253/modified/raspy_exp_id_0000000427_exp_2032_mod_simul_tap.jpg"
    photo_test_huge_aruco_MISSION_1_photo2_mod_simu_tape2 = "/home/bryan/Downloads/mission_20230427_170253/modified/raspy_exp_id_0000000427_exp_2032_mod_simul_tap2.jpg"
    photo_test_huge_aruco_MISSION_1_photo2_mod_simu_sharpened_corner1 = "/home/bryan/Downloads/mission_20230427_170253/modified/raspy_exp_id_0000000427_exp_2032_mod_sharpened_corner1.jpg"

    photo_test_huge_aruco_MISSION_2_phone_photo_trapdoor_test = "/home/bryan/Downloads/mission_20230429_000501"


    photo_test_huge_aruco_MISSION_1_shantanu_god = "/home/bryan/Downloads/mission_20230427_170253/arucos"

    # Dir input
    pathinput = "/home/bryan/Downloads/mission_20230429_111535/"

    # Call main function
    if os.path.isdir(pathinput):
        main(general_path=pathinput,
            id_wanted=7,
            rotate=cv2.ROTATE_90_CLOCKWISE)
    else:
        photo_analyzer(filename=pathinput,
                       id_wanted=7,
                       show=True)
