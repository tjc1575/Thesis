#!/usr/local/bin/python3
"""
	Filename: preprocess.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Preprocess a single participant's data splitting EEG and HR files into
	files that are more easily worked with. Handles naming and file matching
	based on directory structure
"""
from argparse import ArgumentParser
from os import path, walk
from os.path import normpath

from datetime import *
from preprocessEEG import preprocessEEG, partitionEEG, writeChannelData
from preprocessHR import preprocessHR, partitionHR, writeData

from matlab.engine import start_matlab

def main():
	"""
		Run the preprocess functionality on each of the participant directories. Some of the 
		values for the current study are hard coded into this file for ease of use.
	"""
	parser = ArgumentParser()
	parser.add_argument("inputDir")
	parser.add_argument("outputDir")
	
	args = parser.parse_args()
	directory = args.inputDir
	outputDirectory = args.outputDir
	
	intervalSize = 5
	trialLength = 600

	# Start a matlab instance to speed up repeated processes
	eng = start_matlab()

	participantIds = [ '001', '002', '003', '004', '005', '006', '007', '008']
	for participantId in participantIds:
		participantDir = path.join( directory, participantId )
		preprocess( participantDir, outputDirectory, intervalSize, trialLength, eng )
	
	eng.quit()

def preprocess( directory, outputDirectory, intervalSize, trialLength, eng = None ):
	"""
		Preprocess both EEG and HR data from all conditions, trials, and tasks
		for a single participant whose data is stored in directory. A matlab engine
		can be passed to prevent overhead from repeatedly starting.
	"""
	
	# All possible task and condition values
	tasks = ['matb', 'rantask' ]
	conditions = [ 'cond1', 'cond2', 'cond3' ]
	
	
	# Iterate through the task and condition combinations, preprocessing each directory
	for task in tasks:
		taskDirectory = path.join( directory, task )
		for condition in conditions:
			conditionDirectory = path.join( taskDirectory, condition )
			preprocessDirectory( conditionDirectory, outputDirectory, intervalSize, trialLength, eng )
	
def preprocessDirectory( directory, outputDirectory, intervalSize, trialLength, eng = None ):
	"""
		Preprocess a condition directory. Each directory should store
		data for two trials, as well as a performance subdirectory.
		Absolute path should be passed, so that additional information
		can be pulled from the directory structure.
	"""
	
	# Retrieve the condition from the path structure
	remainingPath, condition = path.split( normpath(directory) )
	
	# Retrieve the task from the path structure
	remainingPath, task = path.split( normpath( remainingPath ) )
	
	# Retrieve the participant id from the path structure
	_, participantId = path.split( normpath( remainingPath ) )
	
	# Get a list of all files in the directory
	_, _, filenames = next( walk( directory ) )
	
	# Split .dat (HR) files from .edf (EEG) files
	hr_files = []
	eeg_files = []
	for filename in filenames:
		if ".dat" in filename:
			hr_files.append( filename )
			continue
			
		if ".edf" in filename:
			eeg_files.append( filename )
			continue
	
	# Sort files since trial1 files should have an earlier name than trial2 files
	hr_files.sort()
	eeg_files.sort()
	
	# Generate trial start times from the performance directory logs
	startTimes = findStartTimes( path.join( directory, 'perf' ), task )
	
	# Build a portion of the output directory path based on participant id
	outputDirectory = path.join( outputDirectory, participantId )
	
	preprocessedData = []
	
	# Preprocess data file, assumes there are the same number of hr as eeg files,
	# first file is skipped because it should always be the baseline
	trial = 1
	for index in range(1, len( hr_files ) ):
		# Create output directory for the trial
		trialOutput = path.join( outputDirectory, task + "-" + condition+ "-" + str(trial) )
		
		hr_data = preprocessHR( path.join( directory, hr_files[index] ) )
		
		eeg_data = preprocessEEG( path.join( directory, eeg_files[index]), trialOutput, eng )
		
		# Create trial structure containing the relevant information
		preprocessedData.append( {"hr":hr_data, "eeg":eeg_data, "output":trialOutput, "startTime":startTimes[index-1]})
		
		trial += 1
	
	
	baselineAverage = computeHRBaseline( path.join( directory, hr_files[0] ) )
	
	# Partition and write out the trial data
	for trialData in preprocessedData:
		partitionTrial( trialData, intervalSize, trialLength )
		
		# Write baseline average out to a file in the trial directory
		with open( path.join( trialData['output'], "baselineHR.txt"), 'w' ) as fout:
			fout.write(str(baselineAverage) + '\n')
		
def partitionTrial( preprocessedData, intervalSize, trialLength ):
	"""
		Partition the preprocessed data into intervals of the desired length. 
	"""
	eegData = preprocessedData['eeg']
	hrData = preprocessedData['hr']
	trialStart = preprocessedData['startTime']
	outputDirectory = preprocessedData['output'] 
	
	startTime = findPartitionStart( eegData, hrData, trialStart )
	
	# Run the respective partitioning algorithms
	partitionedEEG = partitionEEG( eegData, startTime, intervalSize, trialLength )
	partitionedHR = partitionHR( hrData, startTime, intervalSize, trialLength )
	
	# Write the data out to files
	writeChannelData( partitionedEEG, outputDirectory )
	writeData( partitionedHR, outputDirectory )
	
	
def findPartitionStart( eeg_data, hr_data, trial_start ):
	"""
		Find the start time for the partitioning of the data. The start time
		for the partitioning is determined by finding the first time after 
		the trial start for which the eeg and hr data line up.
	"""
	startTime = None
	
	# Start eeg at 1 because the first entry is the header information
	eeg_index = 1
	
	hr_index = 0
	
	# While a suitable start time has not been found
	while startTime == None:
		# Try an hr time to a precision of seconds
		hr_time = hr_data[hr_index][0].time()
		hr_time = datetime(100, 1, 1, hr_time.hour, hr_time.minute, hr_time.second).time()
	
		# Try an eeg time to a precision of seconds
		eeg_time = datetime.strptime( eeg_data[eeg_index][0],'%H:%M:%S:%f' ).time()
		eeg_time = datetime(100, 1, 1, eeg_time.hour, eeg_time.minute, eeg_time.second).time()
		
		# If a time is before the start of the trial, try again
		if hr_time < trial_start:
			hr_index += 1
			continue
		if eeg_time < trial_start:
			eeg_index += 1
			continue
			
		# Try to match the times, if not, shift a time to the next valid time
		if  hr_time == eeg_time :
			startTime = hr_time
		elif hr_time > eeg_time:
			eeg_index += 1
		else:
			hr_index += 1
			
		return startTime
	
	
def findStartTimes( directory, task ):
	"""
		Generate the list of start times for the trials, based on file / directory names.
		Slightly different procedures are used depending on whether the performance directory
		is for MATB or RanTask.
	"""
	startTimes = []
	
	# Generate the subdirectories and filenames in the perf directory
	_, dirNames, filenames = next( walk( directory ) )
	
	# Filter filenames so that only '.dat' files are included ( remove meta and hidden files )
	filenames = [ele for ele in filenames if '.dat' in ele] 
	
	if task == "matb":
		dirNames.sort()
		for dirName in dirNames:
			startTimes.append( findStartTimeMATB( path.join(directory, dirName ) ) )
	elif task == "rantask":
		filenames.sort()
		for filename in filenames:
			startTimes.append( findStartTimeRanTask( path.join(directory, filename ) ) )
	
	return startTimes
	
def findStartTimeMATB( directory ):
	"""
		Returns the start time for the trial defined by the 
		given MATB performance directory.
	"""
	# Generate all the files of the given directory
	_, _, filenames = next( walk(directory) )
	
	eventLogFilename = None
	
	# Iterate through filenames, looking for the event log file
	for filename in filenames:
		if "Master_Event_Log" in filename:
			 eventLogFilename = path.join( directory, filename )
			 
	startTime = None
	
	with open( eventLogFilename ) as fin:
		
		# Look through the file for the User Start event
		line = fin.readline()
		while "User Start" not in line:
			line = fin.readline()
		
		# Pull the time the event was logged
		contents = line.strip().split('\t')
		startTimeStr = contents[0]
		startTime = datetime.strptime( startTimeStr,'%H:%M:%S:%f' ).time()
		
	return startTime
	
def findStartTimeRanTask( filename ):
	"""
		Returns the start time for the trial defined by the 
		given RanTask log file.
	"""
	startTime = None
	
	with open( filename ) as fin:
		lines = fin.readlines()
		
		# Start time is logged on the second line of the file
		startTimeStr = lines[1].strip()	
		startTime = datetime.strptime( startTimeStr, '%H:%M:%S.%f' ).time()
	return startTime

def computeHRBaseline( baselineFilename ):
	"""
		Compute and return the average heart rate value from the 
		baseline heart rate data.
	"""
	hrSum = 0
	hrEntries = 0
	
	lines = None
	with open( baselineFilename ) as fin:
		lines = fin.readlines()
	
	hrEntries = len(lines)
	
	# Cut off leading and trailing data that is likely to be noisy
	boundary = hrEntries//5
	lines = lines[ boundary:-boundary ]
	
	for line in lines:
		# Pull hr value out of the entry
		contents = line.strip().split(' | ')
		value = float( contents[1] )
		
		hrSum += value
		
	# Update the number of entries after the cut
	hrEntries = len(lines)
	
	return hrSum / hrEntries
	
if __name__ == '__main__':
	main()