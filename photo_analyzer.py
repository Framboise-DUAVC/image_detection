import cv2
import numpy as np

good_ones = [7, 97, 216, 222, 184]

def photo_analyzer(frame, filename, id_wanted, show=False, output=None):
    # Local auxiliary variable
    trigger = False

    if frame is None:
        frame = cv2.imread(filename)

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
    parameters = cv2.aruco.DetectorParameters_create()
    parameters.errorCorrectionRate = 2.0
    parameters.minMarkerPerimeterRate = 0.06200000000000003
    # cv2.aruco.Dictionary_readDictionary(1, dictionary)
    # detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    # print(dictionary)
    markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(gray_image, dictionary,
                                                                           parameters=parameters)
    # frame_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), markerCorners, markerIds)

    if markerIds is not None:
        for id in markerIds:
            if id in good_ones:
                trigger = True

    if show or output is not None:
        # plt.figure()
        # plt.imshow(frame_markers, origin="upper")
        if markerIds is not None:
            for i in range(len(markerIds)):
                c = markerCorners[i][0]
                # plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "+", label="id={0}".format(markerIds[i]))
                """for points in rejectedImgPoints:
                    y = points[:, 0]
                    x = points[:, 1]
                    plt.plot(x, y, ".m-", linewidth = 1.)"""
        # plt.legend()
        # if show:
        #    # plt.show()
        # if output is not None:
        #    # plt.savefig(output)

    # Save the image
    with open(filename, 'wb') as f_out:
        np.save(f_out, frame)
        np.save(f_out, frame)

    return trigger


# TODO: remove this
if __name__ == '__main__':
    # Call main function
    photo_analyzer(frame=None,
                   filename="/home/bryan/CLionProjects/ISAE/image_detection/test/out/test_capture_avril10_1/raspy_0000000046.jpg",
                   id_wanted=7, show=True)
