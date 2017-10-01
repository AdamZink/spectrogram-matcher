import os
import numpy as np
import cv2

# SOX command to generate spectrogram:
# sox session.wav -n remix 2 rate 6k spectrogram -m -r -X <specWidth> -y <specHeight> -z 80 -o short_song.png

specWidth = 360
specHeight = 512  # instead of 513 because top row is deleted

timeBuckets = 2
frequencyBuckets = 2


image_filename = 'gray.png'

# import spectrogram and format as numpy array
def getReducedSpectrogram(filename, imgWidth, imgHeight, timeBuckets, frequencyBuckets):
	imgFull = cv2.imread(filename, 0) / 255.0
	
	# delete top row so images are evenly divisible by 2, 4, etc
	img = np.delete(imgFull, (0), axis=0)
	#print(str(img.shape) + ' -> ' + str(img))
	
	imgReshape = img.reshape(int(specHeight / frequencyBuckets), frequencyBuckets, int(specWidth / timeBuckets), timeBuckets).sum(axis=3).sum(axis=1)
	#print(str(imgReshape.shape) + ' -> ' + str(imgReshape))
	
	return imgReshape

# Get data for 1 image
image_data = getReducedSpectrogram(os.path.join(os.getcwd(), 'img', 'input', image_filename), specWidth, specHeight, timeBuckets, frequencyBuckets)

print(str(image_data.shape) + ' -> ' + str(image_data))

