#!/usr/local/bin/python3
"""
	Filename: process.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Process the previously preprocessed EEG and HR data into 
	feature vectors usable by models.
"""

from argparse import ArgumentParser
from os import path, makedirs, walk
from os.path import dirname, realpath, basename, normpath
from matlab.engine import start_matlab

from processEEG import processEEG
from processHR import processHR

import matlab.engine
import pickle
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

def main():
	"""
		Process the whoel directory of participant information and dump the 
		pickle.
	"""
	parser = ArgumentParser()
	parser.add_argument("inputDirectory")
	parser.add_argument("outputDirectory")
	
	args = parser.parse_args()
	inputDirectory = args.inputDirectory
	outputDirectory = args.outputDirectory
	
	eng = matlab.engine.start_matlab()	
	participantIds = [ '001', '002', '003', '004', '005', '006', '007' ]
	
	data = {}
	for participantId in participantIds:
		inDir = path.join( inputDirectory, participantId )
		outDir = path.join( outputDirectory, participantId )
		data[ participantId ] = process( inDir, outDir, eng )
		
	eng.quit()
	
	with safe_open( path.join( outputDirectory, 'features.pickle' ), 'wb' ) as fout:
		pickle.dump( data, fout )

def process( directory, outputDirectory, eng = None ):
	"""
		Process a single participants data into usable feature vectors.
		Different trials for a condition will be collapsed into one dataset.
		Conditions, which will serve as classes for classification models, will
		be added onto the end of the feature vectors.
		Different tasks will still be kept separate.
	"""
	
	data = { "matb":[], "rantask":[] }
	
	# Get a list of all the subdirectories
	_, directories, _ = next( walk( directory ) )
	
	header = None
	
	# Process each subdirectory
	for subDirectory in directories:
		trialData = processDirectory( path.join(directory, subDirectory), 
			outputDirectory, eng )
		
		# Pull header information 
		if header == None:
			header = trialData[0]
		
		# Add the data to the correct task, depending on directory name
		# Do not add the first row since it is the header
		if "matb" in subDirectory:
			data["matb"].extend( trialData[1:] )
		elif "rantask" in subDirectory:
			data["rantask"].extend( trialData[1:] )
	
	data['matb'].insert( 0, header )
	data['rantask'].insert( 0, header )
	
	writeData( data['matb'], path.join( outputDirectory, 'matb_combined.txt' ) )
	writeData( data['rantask'], path.join( outputDirectory, 'rantask_combined.txt' ) )
	
	return data
			
def processDirectory( directory, outputDirectory, eng = None ):
	"""
		Process a single condition / trial directory into a feature vector.
		A path structure is assumed that designates the condition.
	"""
	
	eegData = processEEG( directory, outputDirectory, eng )
	hrData = processHR( directory, outputDirectory )
	
	# Determine condition from the directory name to label class
	directoryName = basename( normpath(directory) )
	components = directoryName.split('-')
	conditionLabel = components[1]
	
	# Convert the label into something more meaningful
	condition = 0
	if conditionLabel == 'cond1':
		condition = "low"
	elif conditionLabel == 'cond2':
		condition = "moderate"
	elif conditionLabel == 'cond3':
		condition = "high"
	
	# Join eeg and hr data together with the label	
	combinedData = [ eegData[0] + hrData[0] + ['Condition'] ]
	
	# eegData and hrData are assumed to have the same number of entries
	for index in range( 1, len(eegData) ):
		combinedData.append( eegData[index] + hrData[index] + [condition] )
		
	return combinedData
	
def writeData( data, outputFilename ):
	"""
		Write the features out to a file. This may not be used
		directly, but allows for consistency checking of the data.
	"""
	with safe_open( outputFilename, 'w' ) as fout:
		for row in data:
			fout.write( str(row[0]) )
			for col in row[1:]:
				fout.write('\t')
				fout.write( str(col) )
			fout.write('\n')
		
if __name__ == '__main__':
	main()
	