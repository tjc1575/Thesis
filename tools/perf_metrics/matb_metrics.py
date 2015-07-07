#!/usr/local/bin/python3
"""
	Filename: matb_metrics.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	
"""

from argparse import ArgumentParser
from os import walk, path, remove


def main():
	parser = ArgumentParser()
	parser.add_argument("dir")
	
	args = parser.parse_args()
	directory = args.dir
	print( calcPerformance( directory ) )

def calcPerformance( directory ):
	for root, dirs, files in walk(directory):
		for filename in files:
			if "Standard_Performance_Summary" in filename:
				desired_file = path.join( root, filename )
				return( processFile( desired_file ) )
		
def processFile( filename ):
	performance_sum = 0
	with open( filename ) as fin:
		event_occur = 0
		correct = 0
		false_alarms = 0
		
		for line in fin:
			if "Event Occurences" in line:
				line = line.strip()
				contents = line.split('\t')
				event_occur = float(contents[9])
				continue
			
			if "True Communications" in line:
				line = line.strip()
				contents = line.split('\t')
				event_occur = float(contents[1])
				continue
			
			if "Correct Responses" in line:
				line = line.strip()
				contents = line.split('\t')
				if len( contents ) > 2:
					correct = float(contents[9])
				else:
					correct = float(contents[1])
				continue
				
			if "False Alarms" in line:
				line = line.strip()
				contents = line.split('\t')
				if len( contents ) > 2:
					false_alarms = float(contents[9])
				else:
					false_alarms = float(contents[1])

				performance_sum += ( correct - false_alarms ) / event_occur
				continue
				
			if "%Time Inside Range" in line:
				line = line.strip()
				contents = line.split('\t')
				performance_sum += float(contents[1])

				continue
	return ( performance_sum / 4) * 100
				
if __name__ == '__main__':
	main()		
			



