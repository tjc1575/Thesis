#!/usr/local/bin/python3
"""
	Filename: preprocessHR.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Preprocess heart rate file. Interpolates any gaps in the data as each
	second should have at least one data entry. End result is a tab separated 
	text file contained heart rate data split into desired intervals. 
"""

from argparse import ArgumentParser
from os import path, makedirs

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

def addSecs(tm, secs):
	"""
		Auxillary function used for adding an offset, in seconds, to a
		given time. Slightly different than other versions of the function
		as it returns a datetime, rather than a time, due to requirements
		later in processing.
	"""
	fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second, tm.microsecond)
	fulldate = fulldate + timedelta(seconds=secs)
	return fulldate

def preprocessHR( inputFilename ):
	"""
		Preprocess the desired input HR text file into a cleaner HR data
		with interpolated data points for smoother data.
	"""
	data = readHRFile( inputFilename )
	data = smooth( data )
	return data
	
def readHRFile( filename ):
	"""
		Read in heart rate logging data. File is set up with the time and then the 
		reading done at that time, separated by ' | '. An 2D array is returned 
		where the first element is the time and the second element is the reading.
	"""
	
	# Initialize data holder
	data = []
	
	with open( filename ) as fin:
		for line in fin:
			contents = line.strip().split( ' | ' )
			
			# Read a time object from the first portion of the line
			timeStr = contents[0]
			time = datetime.strptime( timeStr, '%H:%M:%S' )
			
			reading = float(contents[1])
			data.append( [time, reading] )
			
	return data
	
def smooth( data ):
	"""
		Smooth data so that there is at least one data point per second. If a
		second does not have any data, it is interpolated from the neighboring 
		datapoints. The new list of data is returned, rather than modified in 
		place due to memory reasons.
	"""
	
	# Each datapoint should be no more than 1 second apart, otherwise interpolate
	allowableDiff = 1
	
	# Start at the end of the data and more earlier in time to keep
	# the array manipulation cleaner. 
	i = len(data) - 1
	
	# The last point can't be interpolated so start there
	previousDatapoint = data[-1]
	
	while i > 0: 
		currentDatapoint = data[i-1]
		timeDiff = previousDatapoint[0] - currentDatapoint[0]
		
		# If there is more than a one second difference
		if timeDiff.seconds > allowableDiff:
			# Interpolate the data
			interpData = interpolate( currentDatapoint, previousDatapoint )
			
			# Add the interpolated data into the list after the current datapoint
			data = insert( data, interpData, i )
			
		previousDatapoint = currentDatapoint
		i = i - 1

	return data
			
def interpolate( datapoint1, datapoint2 ):
	"""
		Interpolate data between datapoint1 and datapoint2. Datapoint1 is
		the earlier time. Each datapoint is an array with the time at index 0, 
		and the data at index 1. Returns an array of the interpolated data.
	"""
	# Find the difference in time that must be interpolated, i.e. how many points
	timeDiff = (datapoint2[0] - datapoint1[0]).seconds
	
	# Determine what range should be covered by the interpolation
	valueDiff = datapoint2[1] - datapoint1[1]
	
	# Determine how much the value should change each second
	step = valueDiff / timeDiff
	
	# Interpolation time starts at the first datapoint
	interpTime = datapoint1[0]
	
	# Interpolation value starts at the first datapoint
	interpVal = datapoint1[1]
	
	interpData = []
	
	# For each point to interpolate
	for _ in range( timeDiff ):
		interpTime = addSecs( interpTime, 1 )
		interpVal = interpVal + step
		interpData.append( [interpTime, interpVal] )
	
	return interpData
		
def insert( existingList, subList, index ):
	"""
		Inserts the elements of subList into existingList at the 
		given index. A new list is returned to improve memory 
		usage, as multiple, individual inserts mid-list would result
		in poor performance. The element of existingList at index will
		occur after the inserted elements
	"""
	return existingList[:index] + subList[:] + existingList[index:]
	
def partitionHR( data, startTime, intervalSize, trialLength):
	"""
		Split data into 'intervalSize' segments, starting at 'startTime' and continuing for 'trialLength'
		seconds. The return value is a 32 array organized by time-label and then values for the segment.
	"""
	
	# Create the trial end time based on the start time and desired trial length
	endTime = addSecs( startTime, trialLength ).time()
	
	# Ensure start is only time portion
	start = datetime(100, 1, 1, startTime.hour, startTime.minute, startTime.second).time()
	
	# Set initial interval end time based on the start time and interval size
	end = addSecs( start, intervalSize ).time()
	
	partitionedData = [  ]
	
	# Initialize interval list with the time-label for the first interval
	interval = [  str(start.hour) + ':' + str(start.minute) + ':' + 
		str(start.second) + ":" + str(start.microsecond)]
	
	# Process each line 
	for index in range( len(data) ):
		entry = data[index]
		time = entry[0].time()
		
		# If the trial has been completed, stop processing, dumping any partial trial that may have occurred 
		if time > endTime:
			break
		
		# Ignore data point if it is before the start time ( it is noise to be trimmed ).
		if time >= start:
			
			# If the data point is within the interval frame
			if time < end:
				# Add the data value to the interval data
				interval.append(entry[1])
			else:
				# Add the interval to the main data and start a new interval
				partitionedData.append( interval )
				start = end
				end = addSecs( start, intervalSize ).time()
				interval = [  str(start.hour) + ':' + str(start.minute) + ':' + 
					str(start.second) + ":" + str(start.microsecond)]
				
				# Add the data point that triggered the transition to interval
				interval.append( entry[1] )
					
	return partitionedData
	
def writeData( partitionedData, outputDirectory ):
	"""
		Write heart rate data out to a single tab-separated text file.
	"""
	filename = path.join( outputDirectory, 'hr.txt')
	
	with safe_open( filename, 'w' ) as fout:
		for entry in partitionedData:
			
			# Write out the time label
			fout.write(entry[0])
			
			# Write out each data point of the segment
			for index in range( 1, len(entry) ):
				fout.write( '\t' )
				fout.write( str(entry[index]) )
			
			fout.write('\n')
	
def main():
	parser = ArgumentParser()
	parser.add_argument("inputFilename")
	parser.add_argument("outputDirectory")
	
	args = parser.parse_args()
	inputFilename = args.inputFilename
	outputDirectory = args.outputDirectory
	
	dummyStartTime = datetime(100, 1, 1, 10, 20, 58).time()
	
	preprocessHR( inputFilename, outputDirectory, dummyStartTime, 5, 600 )
	
if __name__ == "__main__":
	main()