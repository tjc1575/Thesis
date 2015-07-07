#!/usr/local/bin/python3
"""
	Filename: preprocessEEG.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Preprocess EEG files, transforming them from a single EDK file 
	to multiple tab-separated text files, one channel per file. Each 
	line in a file consists of a timestamp and all data that falls within
	the sample for the data point.
"""

from argparse import ArgumentParser
from os import path, makedirs
from os.path import basename, normpath, splitext
from matlab.engine import start_matlab
from datetime import *

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
	
def microToMilli( micro ):
	"""
		Simple auxillary function that converts microseconds to 
		milliseconds. Used to prevent errors arising from miscalculations.
	"""
	return micro * 1000

def addMsecs(tm, msecs):
	"""
		Auxillary function used for adding an offset, in milliseconds, to a
		given time.
	"""
	fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second, tm.microsecond)
	msecs = microToMilli( msecs )
	fulldate = fulldate + timedelta(microseconds=msecs)
	return fulldate.time()	

def addSecs(tm, secs):
	"""
		Auxillary function used for adding an offset, in seconds, to a
		given time.
	"""
	fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second, tm.microsecond)
	fulldate = fulldate + timedelta(seconds=secs)
	return fulldate.time()


def preprocessEEG( inputFilename, outputDirectory, startTime, intervalSize, trialLength ):
	"""
		Preprocess the desired input EDK file into multiple channel files.
		inputFilename defines the EEG EDK file to be processed.
		outputDirectory is the location where temporary and final
			result files will be written.
		startTime is the time at which to start pulling samples ( allowing
			for noise at the beginning to be trimmed ).
		intervalSize is the number of seconds of data to be combined into a
			single data point.
		trialLength is the number of seconds the trial is, allowing for trailing
			noise to be trimmed.
	"""
	
	mkdir_p( outputDirectory ) # create directory structure to allow for file creation if necessary
	
	parsedFilename = parseAndRemoveBaseline( inputFilename, outputDirectory )
	data = readChannelFile_Offset( parsedFilename )
	
	# Pull clean filename, i.e. no extension or leading directories, of EEG file
	entryName, _ = splitext( basename( normpath(inputFilename) ) )
	
	# Last component of the split entry name is the time at which the file was created
	# This relies on a specific naming convention used by EPOC software
	entryTimeStr = entryName.split('-')[-1]
	
	# Create time structure from the time encoded in the filename
	entryTime = datetime.strptime( entryTimeStr, '%d.%m.%Y.%H.%M.%S' )
	
	timeExpansion( data, entryTime )
	partitionedData = partitionEEG( data, startTime, intervalSize, trialLength )
	
	writeChannelData( partitionedData, outputDirectory )
	
	
def parseAndRemoveBaseline( inputFilename, outputDirectory ):
	"""
		Parse the specified input EDK file, remove baseline, and write the
		relevant channel data out to a tab-separated text file that can be more
		easily read.
		Returns the name of the file the data was written to.
	"""
	
	outputFilename = path.join( outputDirectory, "eeg_parsed.txt" )
	
	eng = start_matlab()
	eng.ParseEEG( inputFilename, outputFilename, nargout=0)
	eng.quit()
	
	return outputFilename
	
def readChannelFile_Offset( filename ):
	"""
		Read in a tab-separated text file containing EEG information separated by channel. This
		version handles reading the file where time entry is an offset from a start time
		rather than an absolute time. Read in data is returned in a 2-d array.
	"""
	data = []
	with open( filename, 'r' ) as fin:
		line = fin.readline() # Skip processing of header on the first line
		data.append( line.strip().split('\t') )
		for line in fin:
			data.append( line.strip().split('\t') )
	return data
	
def timeExpansion( data, collectionStart ):
	"""
		Expand time values of EEG value from an offset of the data collection start to an 
		absolute time that can be compared to other files. EEG data is stored in an array to
		prevent repeated I/O and processing. CollectionStart is the time from which the entries
		are offset. Time is converted back to a string, even though it may be needed as a time value
		again later, for consistency sake.
	"""
	
	# Process each line except the header in the beginning
	for index in range(1, len(data)):
		cur_time = addMsecs( collectionStart, float(data[index][0]) )
		data[index][0] =  ( str(cur_time.hour) + ':' + str(cur_time.minute) + ':' +
					str(cur_time.second) + ":" + str(cur_time.microsecond) )
	
def partitionEEG( data, startTime, intervalSize, trialLength):
	"""
		Split data into 'intervalSize' segments, starting at 'startTime' and continuing for 'trialLength'
		seconds. The return value is a 3D array organized by time-label, channel, and then value 
		for the channel.
	"""
	
	# Create the trial end time based on the start time and desired trial length
	endTime = addSecs( startTime, trialLength )
	
	# Ensure start is only time portion
	start = datetime(100, 1, 1, startTime.hour, startTime.minute, startTime.second).time()
	
	# Set initial interval end time based on the start time and interval size
	end = addSecs( start, intervalSize )
	
	partitionedData = [ data[0] ]
	
	# Initialize interval list with the time-label for the first interval
	interval = [  str(start.hour) + ':' + str(start.minute) + ':' + 
		str(start.second) + ":" + str(start.microsecond)]
	
	# Process each line except the header in the beginning
	for index in range( 1, len(data) ):
		entry = data[index]
		time = datetime.strptime( entry[0], '%H:%M:%S:%f' ).time()
		
		# If the trial has been completed, stop processing, dumping any partial trial that may have occurred 
		if time > endTime:
			break
		
		# Ignore data point if it is before the start time ( it is noise to be trimmed ).
		if time >= start:
			
			# If the data point is within the interval frame
			if time < end:
				# Add the channel values ( ignoring the timestamp ) to the interval data
				interval.append(entry[1:])
			else:
				# Add the interval to the main data and start a new interval
				partitionedData.append( interval )
				start = end
				end = addSecs( start, intervalSize )
				interval = [  str(start.hour) + ':' + str(start.minute) + ':' + 
					str(start.second) + ":" + str(start.microsecond)]
				
				# Add the data point that triggered the transition to interval
				interval.append( entry[1:])
				
	return partitionedData
	
def writeChannelData( partitionedData, outputDirectory ):
	"""
		Write out partitioned EEG data to files, one channel per file.
	"""		
	
	# Header information for what order channels are in
	header = partitionedData[0]
	
	# Create a list of files, one for each channel
	files = []
	for channelName in header:
		filename = path.join( outputDirectory, channelName + '.txt')
		files.append( safe_open( filename, 'w' ) )
	
	# Process each data point, ignoring the initial header entry
	for datapoint in partitionedData[1:]:
		
		# Write the time out to each file
		for fout in files:
			fout.write( datapoint[0] )
			
		# For each set of values for the given data interval
		for entry in datapoint[1:]:
			
			# Write out the value for each channel to the appropriate file
			for i in range( len(entry) ):
				files[i].write( '\t' + entry[i] )
		
		# Write a new line to each file 
		for fout in files:
			fout.write( '\n' ) 
	
	# Close all the files
	for fout in files:
		fout.close()
	
	
	
def main():
	parser = ArgumentParser()
	parser.add_argument("inputFilename")
	parser.add_argument("outputDirectory")
	
	args = parser.parse_args()
	inputFilename = args.inputFilename
	outputDirectory = args.outputDirectory
	
	dummyStartTime = datetime(100, 1, 1, 10, 21, 7).time()
	
	preprocessEEG( inputFilename, outputDirectory, dummyStartTime, 5, 600 )
	
if __name__ == "__main__":
	main()