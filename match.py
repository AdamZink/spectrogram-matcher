import os, sys
import numpy as np
import cv2

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


specWidth = 360
specHeight = yAxisPixels - 1  # will delete top row of data later so height is evenly divisible by 2


timeBuckets = int(specWidth)
frequencyBuckets = int(specHeight)

if (timeBuckets == 0 or specWidth % timeBuckets != 0):
	sys.exit('ERROR - timeBuckets is not valid for specWidth')

if (frequencyBuckets == 0 or specHeight % frequencyBuckets != 0):
	sys.exit('ERROR - frequencyBuckets is not valid for specHeight')
	
timeBucketWidth = int(specWidth / timeBuckets)
frequencyBucketHeight = int(specHeight / frequencyBuckets)


image_filename = 'light_gray.png'

# import spectrogram and format as numpy array
def getReducedSpectrogram(filename, imgWidth, imgHeight, imgSectionWidth, imgSectionHeight):
	# read image as monochrome and normalize to values between 0 and 1
	imgNormalized = cv2.imread(filename, 0) / 255.0
	
	# delete top row so image height is evenly divisible by 2, 4, etc
	imgLog = np.delete(imgNormalized, (0), axis=0)
	#print(str(imgLog.shape) + ' -> ' + str(imgLog))
	
	# convert decibel values to linear scale
	# use 0 as linear value if spectrogram is black
	imgLinear = np.where(imgLog == 0, 0, 10.0 ** ((imgLog - 1.0) * zMultipleOfTen))
	#print(str(imgLinear.shape) + ' -> ' + str(imgLinear))
	
	if(imgSectionWidth == 1 and imgSectionHeight == 1):
		return imgLinear
		
	else:
		imgReshape = imgLinear.reshape(int(imgHeight / imgSectionHeight), imgSectionHeight, int(imgWidth / imgSectionWidth), imgSectionWidth).mean(axis=3).mean(axis=1)
		#print(str(imgReshape.shape) + ' -> ' + str(imgReshape))

		return imgReshape


# Get data for 1 image
image_data = getReducedSpectrogram(os.path.join(os.getcwd(), 'img', 'input', image_filename), specWidth, specHeight, timeBucketWidth, frequencyBucketHeight)

print(str(image_data.shape) + ' -> ' + str(image_data))

