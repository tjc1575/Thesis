#!/usr/local/bin/python3
"""
	Filename: processEEG.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Process EEG channel files into spectral band information organized in a 
	manner than can easily condensed into a feature map for classification.
"""
from argparse import ArgumentParser
from os import path, makedirs
from os.path import dirname, realpath, basename, normpath
from matlab.engine import start_matlab

import matlab.engine

import errno

# Taken from http://stackoverflow.com/a/600612/119527
def mkdir_p(filepath):
	"""
		Creates the necessary directories and subdirectories to 
		have the specified folder / path structure
	"""
	try:
		makedirs(filepath)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and path.isdir(filepath):
			pass
		else: 
			raise

# Modified from http://stackoverflow.com/a/23794010
def safe_open(filepath, mode):
	"""
		This is used for opening up files for writing when the
		path may not exist and need to be created.
	"""
	mkdir_p(path.dirname(filepath))
	return open(filepath, mode)

def processEEG( directory, outputDirectory, eng = None ):
	"""
		Process a directory full of EEG channel information. The 
		information is then combined into a feature map. A matlab 
		instance can be passed in to reduce overhead.
	"""
	channels = ['AF3', 'AF4', 'F3', 'F4', 'F7', 'F8', 'FC5', 'FC6', 'O1', 
		'O2', 'P7', 'P8', 'T7', 'T8']
		
	bands = [ 'delta', 'theta', 'alpha', 'beta', 'gamma' ]
	
	data = []
		
	for channel in channels:
		channelData = processChannelFile( path.join( directory, channel+".txt" ), eng )
		data.append( channelData )
		
	# It is assumed that all channels contain the same number of entries
	# which should be true since they were pulled from the same master
	numEntries = len(data[0])
	
	numChannels = len(channels)
	numBands = len(bands)
		
	# List for holding the restructured data to remove nesting
	# Initialize to prevent continuous resizing. Each row
	# needs room for all bands of all channels. There is
	# one extra row for the header
	orderedData = [ [None]*(numChannels * numBands) for _ in range(numEntries+1) ]
	
	for channelIndex in range( len(channels) ):
		for bandIndex in range( len(bands) ):
			# Calculate what column we are at based on the channel
			# and band we are using
			colIndex = (channelIndex * numBands) + bandIndex
			
			# Put in header information
			orderedData[0][colIndex] = channels[channelIndex]+'_'+bands[bandIndex]
			
			# Add the entry data
			for index in range( numEntries ):
				# Index + 1 because the header offsets the rest of the entries
				orderedData[index+1][colIndex] = data[channelIndex][index][bandIndex]
			
	# Figure out what the file should be named based on the directory	
	condition = basename( normpath(directory) )
	outputFilename = path.join( outputDirectory, condition+"eeg.txt" )
	writeData( orderedData, outputFilename )
	
	return orderedData
		
def processChannelFile( filename, eng = None ):
	"""
		Process a single channel file, creating band information
		for each segment of data. A matlab engine can be passed
		in to reduce overhead. 
		Returns a 2D list of band information in the order: [ delta, theta, 
		alpha, beta, gamma ] for each time interval
	"""
	
	existing = True
	
	# Create a new matlab instance if one was not provided
	if eng == None:
		eng = start_matlab()
		existing = False
		
	# Add the current directory to the matlab path so that the function can be found
	eng.addpath( dirname(realpath(__file__)) )
	
	channelData = []
	with open( filename ) as fin:
		for line in fin:
			contents = line.strip().split('\t')
			
			# Remove the time stamp
			contents.pop(0)
			
			# Cast the elements to floats
			values = [ float(ele) for ele in contents ]
			
			# Make a matlab array from the data
			mArray =  matlab.double(values)
			bands = eng.Bandify( mArray, nargout = 5 )
			eng.clc(nargout = 0)
			eng.clear(nargout = 0)
			
			channelData.append( bands )
		
	# Shutdown matlab if it was created here	
	if not existing:
		eng.quit()
		
	return channelData
	
def writeData( data, outputFilename ):
	"""
		Write the EEG features out to a file. This may not be used
		directly, but allows for consistency checking of the data.
	"""
	with safe_open( outputFilename, 'w' ) as fout:
		for row in data:
			fout.write( str(row[0]) )
			for col in row[1:]:
				fout.write('\t')
				fout.write( str(col) )
			fout.write('\n')
				 
				 
def main():
	parser = ArgumentParser()
	parser.add_argument("inputDirectory")
	parser.add_argument("outputDirectory")
	
	args = parser.parse_args()
	inputDirectory = args.inputDirectory
	outputDirectory = args.outputDirectory
	
	eng = matlab.engine.start_matlab()
	processEEG( inputDirectory, outputDirectory, eng )
	eng.quit()
	
if __name__ == '__main__':
	main()