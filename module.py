import cv2
def resizeImage(image, magnitude):
    imageHeight, imageWidth = image.shape[:2]
    resizedImage = cv2.resize(image,
                              (int(imageWidth * magnitude), int(imageHeight * magnitude)))
    return resizedImage
    
def cross_correlation(array1, array2):
    import array
    import pylab as pl
    nx = len(array1)
    ny = len(array2)
    if nx != ny:
        print "Error: lengths of two lists does not math each other."
        
    cross_corr = array.array('f')
    for i in range(nx):
        sum = 0.0
        for j in range(nx - i):
            sum = sum + float(array1[j]) * float(array2[i+j])
        cross_corr.append(sum/float(nx-i))

    return cross_corr

def bandpassFilter(wave):
    import header as hd
    import scipy.signal as sig
    import numpy as np
    #fe1 = 120. / (hd.maxBpm * hd.videoFps)
    #fe2 = 120. / (hd.minBpm * hd.videoFps)
    fe2 = (2. * hd.maxBpm) / (60 * hd.videoFps)
    fe1 = (2. * hd.minBpm) / (60 * hd.videoFps)
    b, a = sig.butter(2, [fe1, fe2], 'bandpass')
    filteredValue = sig.filtfilt(b,a,wave)
    return filteredValue
