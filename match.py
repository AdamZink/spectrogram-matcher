import os
import numpy as np
import cv2

# SOX command to generate spectrogram:
# sox session.wav -n remix 2 rate 6k spectrogram -m -r -X <specWidth> -y <specHeight> -z 80 -o short_song.png

specWidth = 360
specHeight = 513
splitSize = 360

image_filename = 'sin_G4.png'

# import spectrogram and format as numpy array
def get1dSpectrogramSlices(filename, imgWidth, numSlices=1):
	img = cv2.imread(filename, 0) / 255.0
	slicesArray = np.split(img, int(imgWidth/splitSize), axis=1)
	resultArray = np.empty(shape=(0, splitSize*specHeight))
	sliceCount = 0
	for slice in slicesArray:
		slice = slice.flatten()
		slice = np.expand_dims(slice, axis=0)
		resultArray = np.append(resultArray, slice, axis=0)
		sliceCount += 1
		if (sliceCount >= numSlices):
			break
	return resultArray

# Get data for 1 image
image_data = get1dSpectrogramSlices(os.path.join(os.getcwd(), 'img', 'input', image_filename), specWidth, int(specWidth / splitSize))

print(str(image_data.shape) + ' -> ' + str(image_data))

