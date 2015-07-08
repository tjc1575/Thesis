#!/usr/local/bin/python3
"""
	Filename: processHR.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Process the HR file, producing average hr and HRV for each
	time segment, modified by the baseline.
"""

from argparse import ArgumentParser
from os import path, makedirs
from os.path import dirname, realpath, basename, normpath


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

def processHR( directory, outputDirectory ):
	"""
		Process a directory full of hr information. The 
		information is then combined into a feature map.
	"""
	
	hrFilename = path.join( directory, "hr.txt" )
	hrBaselineFilename = path.join( directory, "baselineHR.txt" )
	
	hrData = readHRFile( hrFilename )
	baseline = readBaselineFile( hrBaselineFilename )
	
	adjustForBaseline( hrData, baseline )
	
	features = computeFeatures( hrData )
	
	# Figure out what the file should be named based on the directory	
	condition = basename( normpath(directory) )
	outputFilename = path.join( outputDirectory, condition+"hr.txt" )
	writeData( features, outputFilename )
	
	return features
	
	
	
def readBaselineFile( filename ):
	"""
		Read and return the baseline hr value from the 
		baseline text file.
	"""
	
	baselineHR = 0
	
	with open( filename ) as fin:
		line = fin.readline()
		baselineHR = float( line.strip() )
		
	return baselineHR

def readHRFile( filename ):
	"""
		Read the hr file and return the data, minus the time
		labels of each data entry.
	"""
	
	data = []
	
	with open( filename ) as fin:
		for line in fin:
			contents = line.strip().split('\t')
			
			# Cut off the first element and cast the rest to float
			data.append( [ float(ele) for ele in contents[1:] ] )
	
	return data

def adjustForBaseline( data, baseline ):
	"""
		Subtract the baseline value from each entry in data. A constant
		is then added to ensure all adjusted values are still positive.
	"""
	
	# 20 should be large enough to keep all values positive
	OFFSET = 20
	
	for i in range( len( data ) ):
		for j in range( len(data[i]) ):
			data[i][j] = ( data[i][j] - baseline ) + OFFSET
			
			# Ensure the values are all positive
			if data[i][j] <= 0:
				raise Error( "Non-positive hr" )
				
def computeFeatures( data ):
	"""
		Compute the average hr and hrv features for each entry.
	"""
	
	features = [ ['average_hr', 'hrv'] ]
	
	for entry in data:
		sumHR = 0
		numEntries = len(entry)
		
		for value in entry:
			sumHR += value
		
		meanHR = sumHR / numEntries
		stdDevHR = computeStandardDeviation( entry, meanHR )
		hrv = stdDevHR / meanHR
		
		features.append( [meanHR, hrv] )
	
	return features
		

def computeStandardDeviation( values, mean ):
	"""
		Compute the standard deviation of the samples given the sample
		values and the mean of the sample.
	"""
	
	n = len(values)
	
	summation = 0
	for value in values:
		summation += ( ( value - mean ) ** 2)
	
	return (summation / (n-1)) ** (1/2)
	
def writeData( data, outputFilename ):
	"""
		Write the HR features out to a file. This may not be used
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
	
	processHR( inputDirectory, outputDirectory )
	
if __name__ == '__main__':
	main()