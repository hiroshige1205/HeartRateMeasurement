def sinWaveFilter(rawQueue, waveFps, waveBpm, filterCycle):
    import numpy as np
    import math
    filterNumber = int(round(60. * waveFps / waveBpm) * filterCycle)
    rawQueueSize = rawQueue.size
    queue = rawQueue[rawQueueSize - filterNumber : rawQueueSize]
    sinFilter = np.zeros(filterNumber)
    for i in np.arange(filterNumber):
        sinFilter[i] = math.cos((i + 1) * 2 * math.pi / filterNumber)
    return np.sum(sinFilter * queue)

def hilbertFilter(rawQueue):
    import header as hd
    import scipy.signal as sig
    import numpy as np
    fe1 = 120. / (hd.maxBpm * hd.videoFps)
    fe2 = 120. / (hd.minBpm * hd.videoFps)
    b, a = sig.butter(2, [fe1, fe2], 'bandpass')
    filteredValue = sig.filtfilt(b,a,rawQueue)
    hilbertedValue = sig.hilbert(filteredValue)
    greenPhase = np.angle(hilbertedValue)
    return greenPhase, filteredValue
    
