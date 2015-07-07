#!/usr/local/bin/python3

from argparse import ArgumentParser
from os import walk, path, remove


def main():
	parser = ArgumentParser()
	parser.add_argument("filename")
	
	args = parser.parse_args()
	filename = args.filename
	print( calcPerformance( filename ) )

def calcPerformance( filename ):
	performance = 0
	
	with open( filename ) as fin:
		lines = fin.readlines()
		expected_line = lines[0]
		count_low_line  = lines[-4]
		count_medium_line  = lines[-3]
		count_high_line  = lines[-2] 
		response_line = lines[-1]
		
		expected_contents = expected_line.strip().split()
		expected_low = int(expected_contents[1][:-1])
		expected_medium = int(expected_contents[2][:-1])
		expected_high = int(expected_contents[3])
		
		count_low_contents = count_low_line.strip().split(": ")
		count_medium_contents = count_medium_line.strip().split(": ")
		count_high_contents = count_high_line.strip().split(": ")
		
		count_low = int(count_low_contents[1])
		count_medium = int(count_medium_contents[1])
		count_high = int(count_high_contents[1])
		
		response_contents = response_line.strip().split()
		correct = int(response_contents[1][:-1])
		false_pos = int(response_contents[4])
		
		total_targets = 0
		if expected_low > 0:
			total_targets += count_low // expected_low
		if expected_medium > 0:
			total_targets += count_medium // expected_medium
		if expected_high > 0:
			total_targets += count_high // expected_high

		performance = (correct - false_pos) / total_targets
		return performance
		
				
if __name__ == '__main__':
	main()		
			



