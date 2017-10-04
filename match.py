import os, sys
import numpy as np
import cv2

# SOX command to generate spectrogram:
# sox session.wav -n remix 2 rate 6k spectrogram -m -r -X <specWidth> -y <specHeight+1> -z 80 -o short_song.png

specWidth = 360
specHeight = 512  # instead of 513 because top row is deleted

timeBuckets = int(specWidth)
frequencyBuckets = int(specHeight)

if (timeBuckets == 0 or specWidth % timeBuckets != 0):
	sys.exit('ERROR - timeBuckets is not valid for specWidth')

if (frequencyBuckets == 0 or specHeight % frequencyBuckets != 0):
	sys.exit('ERROR - frequencyBuckets is not valid for specHeight')
	
timeBucketWidth = int(specWidth / timeBuckets)
frequencyBucketHeight = int(specHeight / frequencyBuckets)

image_filename = 'gray.png'


# import spectrogram and format as numpy array
def getReducedImage(filename, imgWidth, imgHeight, imgSectionWidth, imgSectionHeight):
	imgFull = cv2.imread(filename, 0) / 255.0
	
	# delete top row so images are evenly divisible by 2, 4, etc
	img = np.delete(imgFull, (0), axis=0)
	#print(str(img.shape) + ' -> ' + str(img))
	
	if(imgSectionWidth == 1 and imgSectionHeight == 1):
		return img
		
	else:
		imgReshape = img.reshape(int(imgHeight / imgSectionHeight), imgSectionHeight, int(imgWidth / imgSectionWidth), imgSectionWidth).mean(axis=3).mean(axis=1)
		#print(str(imgReshape.shape) + ' -> ' + str(imgReshape))

		return imgReshape

# Get data for 1 image
image_data = getReducedImage(os.path.join(os.getcwd(), 'img', 'input', image_filename), specWidth, specHeight, timeBucketWidth, frequencyBucketHeight)

print(str(image_data.shape) + ' -> ' + str(image_data))

