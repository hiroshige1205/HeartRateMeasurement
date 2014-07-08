import video
import cv2

capture = video.openCamera(1)
while True:
    ret, frame = capture.read()
    if not ret:
        print 'could not'
        exit()

    cv2.imshow('Captured Frame', frame)
    inputkey = cv2.waitKey(100)
    c = chr(inputkey & 255)
    if c in ['q',chr(27)]:
        break

if(capture.isOpened()):
    capture.release()

cv2.destroyAllWindows()
