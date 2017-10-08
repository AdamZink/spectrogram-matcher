import os, sys
import numpy as np
import cv2
import scipy.io.wavfile as wf
import scipy.signal as sig
import random

# SOX command to generate spectrogram:
# sox session.wav -n remix 2 rate <soxRate> spectrogram -m -r -X <specWidth> -y <specHeight+1> -z <zAxisDbRange> -o short_song.png
# Note: only include 'remix 2' option if there are left and right channels

# sox: rate generates spectrogram frequency analysis from 0 Hz to (soxRate / 2) Hz
soxRate = int(6e3)
maxSpecFrequency = int(soxRate / 2.0)

# sox: range 1 - 5000
xAxisPixelsPerSecond = 360

# sox: power of 2, plus 1
yAxisPixels = (2**9) + 1

#sox: range 20 - 180 (keep as multiple of 10 for simplicity)
zMultipleOfTen = 8
zAxisDbRange = 10 * zMultipleOfTen


specWidth = xAxisPixelsPerSecond
specHeight = yAxisPixels - 1  # will delete top row of data later so height is evenly divisible by 2

specDurationInSeconds = 1.0


timeBuckets = 1 #int(specWidth)
frequencyBuckets = int(specHeight)

if (timeBuckets == 0 or specWidth % timeBuckets != 0):
	sys.exit('ERROR - timeBuckets is not valid for specWidth')

if (frequencyBuckets == 0 or specHeight % frequencyBuckets != 0):
	sys.exit('ERROR - frequencyBuckets is not valid for specHeight')
	
timeBucketWidth = int(specWidth / timeBuckets)
frequencyBucketHeight = int(specHeight / frequencyBuckets)


image_filename = 'sin_G4.png'

# import spectrogram and format as numpy array
def getReducedSpectrogram(filename, imgWidth, imgHeight, imgSectionWidth, imgSectionHeight):
	# read image as monochrome and normalize to values between 0 and 1
	imgNormalized = cv2.imread(filename, 0) / 255.0
	
	# delete top row so image height is evenly divisible by 2, 4, etc
	imgLog = np.delete(imgNormalized, (0), axis=0)
	#print(str(imgLog.shape) + ' -> ' + str(imgLog))
	
	# convert decibel values to linear scale
	# use 0 as linear value if spectrogram is black
	imgRelativeLoudness = np.where(imgLog == 0, 0, 2.0 ** ((imgLog - 1.0) * zMultipleOfTen))
	#print(str(imgLinear.shape) + ' -> ' + str(imgLinear))
	
	if(imgSectionWidth == 1 and imgSectionHeight == 1):
		return imgRelativeLoudness
		
	else:
		imgReshape = imgRelativeLoudness.reshape(int(imgHeight / imgSectionHeight), imgSectionHeight, int(imgWidth / imgSectionWidth), imgSectionWidth).mean(axis=3).mean(axis=1)
		#print(str(imgReshape.shape) + ' -> ' + str(imgReshape))

		return imgReshape


# Get data for 1 image
image_data = getReducedSpectrogram(os.path.join(os.getcwd(), 'img', 'input', image_filename), specWidth, specHeight, timeBucketWidth, frequencyBucketHeight)

#print(str(image_data.shape) + ' -> ' + str(image_data))

samplesPerSecond = 44100


def isMusicalFrequencyBucket(lowerFrequency, upperFrequency):
	fundamentalFrequencies = [
		261.63,
		293.66,
		329.63,
		349.23,
		392,
		440,
		493.88,
		523.25
	]
	numOvertones = 5
	musicalFrequencies = fundamentalFrequencies
	for i in range(0, numOvertones):
		musicalFrequencies += [x*(i+2) for x in fundamentalFrequencies]
	
	return len([f for f in musicalFrequencies if f >= lowerFrequency and f < upperFrequency]) > 0
	

def getSamples(amplitudeData, amplitudeValuesPerSecond, durationInSeconds, maxFrequency):
	frequencyBuckets, timeBuckets = amplitudeData.shape
	
	frequencySplits = np.linspace(0, maxFrequency, frequencyBuckets + 1)
	frequencyBucketLowerBounds = frequencySplits[:-1]
	frequencyBucketUpperBounds = frequencySplits[1:]
	frequencyBucketTuples = list(zip(np.flip(frequencyBucketLowerBounds, axis=0), np.flip(frequencyBucketUpperBounds, axis=0)))
	
	#print(frequencyBucketTuples)
	
	t = np.arange(durationInSeconds * samplesPerSecond)
	
	sampleData = np.sin(2.0 * np.pi * t * ((1.0 * 0) / samplesPerSecond))

	amplitudeIndex = 0
	for lowerFrequency, upperFrequency in frequencyBucketTuples:
	
	
		amplitude = 0
		if(isMusicalFrequencyBucket(lowerFrequency, upperFrequency)):
			amplitude = amplitudeData[amplitudeIndex][0]
		#randomPhaseShift = random.random() * 10000.0  # better way to do this?
		
		midpointFrequency = (lowerFrequency + upperFrequency) / 2.0
		
		# frequencyData = amplitude * sin( frequency * time + phase shift )
		#frequencyData = amplitudeData[amplitudeIndex][0] * np.sin((2.0 * np.pi * t * ((1.0 * frequency) / samplesPerSecond)) + randomPhaseShift)
		frequencyData = amplitude * np.sin(2.0 * np.pi * t * ((1.0 * midpointFrequency) / samplesPerSecond))
		
		sampleData = np.add(sampleData, frequencyData)
		
		amplitudeIndex += 1
		
	return sampleData
	
	
def normalizeForWav(data, maxAmplitude):
	return np.int16(data / np.max(np.abs(data)) * (maxAmplitude * (32767 - 100)))


# Calculate audio samples for image data

samples = getSamples(image_data, specWidth, specDurationInSeconds, maxSpecFrequency)

result = normalizeForWav(samples, 0.1)

print(str(result.shape) + ' -> ' + str(result))


wavRelativeDir = 'wav'

filename = os.path.join(wavRelativeDir, 'clean_' + str(timeBuckets) + '_' + str(frequencyBuckets) + '.wav')
wf.write(filename, samplesPerSecond, result)
print('Wrote ' + filename)

