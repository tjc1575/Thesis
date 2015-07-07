#!/usr/local/bin/python3
"""
	Filename: metrics.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Perform performance metric calculations for a single participant.
	Uses both the rantask and matb performance metric scripts to 
	calculate the respective performance metrics.

"""

from argparse import ArgumentParser
from os import walk, path, remove
from os.path import basename, normpath, splitext

import matb_metrics as matb
import rantask_metrics as rantask

	
def processParticipant( directory ):
	"""
		Process the performance metrics for a participant, based on 
		the passed directory. Results are output to a csv file in the
		local directory.
	"""
	
	# Figure out participant id based on directory naming
	participantId = basename( normpath(directory) )
	
	# Assumes a standard directory structure
	matbDir = path.join( directory, "matb" )
	rantaskDir = path.join( directory, "rantask" )
	
	# Calculate the performance metric for each task
	perfMap = {}
	perfMap["matb"] = processMATB( matbDir )
	perfMap["rantask"] = processRanTask( rantaskDir )
	
	# Write the performance data out
	writeOutputFull( participantId+".csv", perfMap )
	
def writeOutputFull( filename, perf ):
	"""
		Writes complete performance summary to the desired file. Data for both tasks
		is included in one file, separated by some newlines.
	"""
	with open(filename, 'w') as fout:
		fout.write("MATB\n")
		writeOutputSingle( fout, perf['matb'] )
		
		fout.write('\n')
		fout.write('\n')
		fout.write('\n')
		
		fout.write("RanTask\n")
		writeOutputSingle( fout, perf['rantask'] )
		
		
def writeOutputSingle( fout, perf ):
	"""
		Write performance data for a single task to the desired file. 
	"""
	fout.write("Condition, Trial 1, Trial 2\n")
	
	fout.write("Low")
	if "cond1" in perf:
		for entry in perf["cond1"]:
			fout.write(", " + str(entry) )
	fout.write('\n')
		
	fout.write("Moderate")
	if "cond2" in perf:
		for entry in perf["cond2"]:
			fout.write(", " + str(entry) )
	fout.write('\n')
		
	fout.write("High")
	if "cond3" in perf:
		for entry in perf["cond3"]:
			fout.write(", " + str(entry) )
	fout.write('\n')
		
	
def processMATB( directory ):
	"""
		Process the MATB directory to calculate summary performance
		information for all conditions / trials. Exception handling
		should not be necessary and is only in place so partial
		directories can be processed without crashing.
	"""
	conditions = ["cond1", "cond2", "cond3"]
	perfMap = {}
	try:
		# Each condition has its own directory
		for condition in conditions:
			condDir = path.join( directory, condition )
			perfDir = path.join( condDir, "perf" )
			
			# Generate all the subdirectories of the performance directory
			_, dirNames, _ = next( walk(perfDir) )
			
			# Sort the directories, since trial 1 should have an earlier name than trial 2
			dirNames.sort()
			
			perfMap[condition] = []
			for dirName in dirNames:
				performance = matb.calcPerformance(path.join(perfDir, dirName))
				perfMap[condition].append(performance)
	except:
		pass

	return perfMap
	
def processRanTask( directory ):
	"""
		Process the RanTask directory to calculate summary performance
		information for all conditions / trials. Exception handling
		should not be necessary and is only in place so partial
		directories can be processed without crashing.
	"""
	conditions = ["cond1", "cond2", "cond3"]
	perfMap = {}
	try:
		# Each condition has its own directory
		for condition in conditions:
			condDir = path.join( directory, condition )
			perfDir = path.join( condDir, "perf" )
			
			# Generate all the files of the performance directory
			_, _, fileNames = next( walk(perfDir) )
			
			# Sort the files, since trial 1 should have an earlier name than trial 2
			fileNames.sort()
			
			perfMap[condition] = []
			for fileName in fileNames:
				_, fileExtension = splitext(fileName)
				if fileExtension != ".dat":
					continue
				performance = rantask.calcPerformance(path.join(perfDir, fileName))
				perfMap[condition].append(performance)
	except:
		pass

	return perfMap
			
	
def main():
	parser = ArgumentParser()
	parser.add_argument("dir")
	
	args = parser.parse_args()
	directory = args.dir
	processParticipant( directory )
	
if __name__ == '__main__':
	main()