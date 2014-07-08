def openCamera(cameraid):
    import cv2
    capture = cv2.VideoCapture(cameraid)

    isopen = capture.isOpened()
    if(False == isopen):
        capture.open(cameraid)
        isopen = capture.isOpened()
        if(False == isopen):
            print'Could not open camera.'
            exit()
    return capture
    

def captureWidthHeight(capture):
    import cv2
    imwidth = capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    imheight = capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
    return [imwidth, imheight]
