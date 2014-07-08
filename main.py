import cv2
import video
import time
import faceDetection
import numpy as np
import queueFilter
import serial
import sys
import header as hd
import module

waveFps = 10
waveBpm = 70
filterCycle = 1

argvs = sys.argv
argc = len(argvs)
#is Serial Use ?
#py face.py 1 0
isSerial = False
#use WebCam ? 
#py face.py 0 1
isTurnOver = False
if argc >= 2 and argvs[1] == '1':
    isSerial = True
if argc >= 3 and argvs[2] == '1':
        isTurnOver = True
if isTurnOver:
    capture = video.openCamera(1)
else:
    capture = video.openCamera(0)
[videoWidth, videoHeight] = video.captureWidthHeight(capture)

videoSize = hd.videoSize
if videoSize[0] > videoWidth:
    videoSize[0] = videoWidth
if videoSize[1] > videoHeight:
    videoSize[1] = videoHeight

tempx1 = int((videoWidth - videoSize[0]) / 2)
tempx2 = int((videoWidth + videoSize[0]) / 2)
tempy1 = int((videoHeight - videoSize[1]) / 2)
tempy2 = int((videoHeight + videoSize[1]) / 2)

if isSerial:
    ser = serial.Serial('/dev/tty.usbmodem14141',115200,timeout = 1)

cascade_path = "/usr/local/opt/opencv/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml"
cascade = cv2.CascadeClassifier(cascade_path)
previousTime = time.time()
previousBeatTime = time.time()
previousValue = 1.

queueGreenMean = np.zeros(hd.queueLength)

greenArray = np.arange(0)

beatFlag = False
saveData = np.arange(0)

previousIsFaceDetected = False
isFaceDetected = False
beatCount = 0

previousFaceDetectedTime = time.time()


startBeatTime = 4.
beatCycle = 1.
isBPMcalculated = False

isLEDon = False


while True:
    ret, rawImage = capture.read()
    if not ret:
        print 'Could not capture frame.'
        break
    trimmedImage = rawImage[tempy1:tempy2,tempx1:tempx2,:]
    resizedImage = module.resizeImage(trimmedImage, 1./hd.videoReductionRatio)
    if isTurnOver:
        resizedImage = resizedImage[::-1,::-1,:].copy()
    [faceImage, greenMean, isFaceDetected] = faceDetection.faceDetection(resizedImage.copy(), cascade)
    skinImage = faceDetection.skinDetection(resizedImage)
    print "greenMean is %.3f" % greenMean
    queueGreenMean = np.delete(queueGreenMean, 0)
    queueGreenMean = np.append(queueGreenMean, greenMean)
    greenArray = np.append(greenArray, greenMean)
    filteredValue = queueFilter.sinWaveFilter(queueGreenMean, waveFps, waveBpm, filterCycle)
    greenPhase,temp = queueFilter.hilbertFilter(queueGreenMean)
    if previousValue < 0 and greenPhase[hd.queueLength - 1] > 0:
        nowBeatTime = time.time()
        beatLength = nowBeatTime - previousBeatTime
        if beatLength > 60. / hd.maxBpm:
            previousBeatTime = nowBeatTime
            print "bpm is %d" % int(60./beatLength)
            beatFlag = True
    previousValue = greenPhase[hd.queueLength - 1]

    if isSerial:
        if isFaceDetected:
            if not isLEDon:
                ser.write('xg')
                isLEDon = True
            if not previousIsFaceDetected:
                previousFaceDetectedTime = time.time()

            if (time.time() - previousFaceDetectedTime) > startBeatTime and not isBPMcalculated:
                #module.cross_correlation(queueGreenMean, queueGreenMean)
                filteredQueue = module.bandpassFilter(queueGreenMean)
                xcorr = module.cross_correlation(filteredQueue,filteredQueue)
                maxIndex = np.argmax(xcorr[6:18]) + 6
                if maxIndex > 11 or maxIndex < 8:
                    maxIndex = 10

                beatCycle = maxIndex / 12.
                isBPMcalculated = True
            

            if (time.time() - previousFaceDetectedTime) > startBeatTime + beatCount * beatCycle:
                
                if beatCount < 4:
                    ser.write('ag')
                elif beatCount < 8:
                    ser.write('cg')
                elif beatCount < 12:
                    ser.write('eg')
                else:
                    ser.write('fg')
                beatCount += 1
        else:
            if isLEDon:
                ser.write('yg')
                isLEDon = False
                isBPMcalculated = False
            beatCount = 0

    previousIsFaceDetected = isFaceDetected

    
    if beatFlag:
        faceImage[:,:,2] = faceImage[:,:,2] + 100
        beatFlag = False

    print previousValue
    if hd.isSave:
        if greenArray.size > hd.saveDataLengthMax:
            hilbertWave, filteredWave = queueFilter.hilbertFilter(greenArray)
            np.savetxt(hd.hilbertSaveName, hilbertWave,fmt = "%.3f")
            np.savetxt(hd.waveSaveName, filteredWave,fmt = "%.3f")
            break
        '''
        saveData = np.append(saveData, greenMean)
        if saveData.size > hd.saveDataLengthMax:
            np.savetxt(hd.saveName, saveData)
            break
        '''
    dispImage = module.resizeImage(faceImage, hd.dispMagnificationPower)
    cv2.imshow('Captured Frame', dispImage)
    
    inputkey = cv2.waitKey(10)
    c = chr(inputkey & 255)
    if c in ['q', chr(27)]:
        break

    tempTime = time.time() - previousTime
    maxFpsTime = 1./hd.maxFps
    if maxFpsTime > tempTime:
        time.sleep(maxFpsTime - tempTime)
    nowTime = time.time()
    frameTime = nowTime - previousTime
    previousTime = nowTime
    print "fps is %f.2" % (1./frameTime)
    waveFps = int(1./frameTime)

if(capture.isOpened()):
    capture.release()

cv2.destroyAllWindows()
        


