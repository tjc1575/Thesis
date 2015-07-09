#!/usr/local/bin/python3
"""
	Filename: rfcBuilder.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Generate random forest classifier models for the same participant, same 
	task setup.
"""

import pickle
import errno
import time

import numpy as np

from argparse import ArgumentParser
from os import path, makedirs, walk
from os.path import dirname, realpath, basename, normpath

from numpy import array, argmax, zeros
from sklearn import cross_validation
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
		
def main():
	"""
		Build all the models. Spin off a new process for each participant
		because the ANN library is not multithreaded. Process is used instead
		of thread to leverage multiple cores.
	"""
	parser = ArgumentParser()
	parser.add_argument("inputFilename")
	parser.add_argument("outputDirectory")
	
	args = parser.parse_args()
	inputFilename = args.inputFilename
	outputDirectory = args.outputDirectory
	
	data = pickle.load( open(inputFilename, 'rb') )
	
	tasks = [ 'matb', 'rantask' ]
	participantIds = [ '001', '002', '003', '004', '005', '006', '007' ]
	
	# Record start time so that the elapsed time can be determined
	start_time = time.time()
	
	# Build models for participants in a task
	for task in tasks:
		for participantId in participantIds:
			outputFilename = path.join( outputDirectory, participantId + '-' + task + '.txt' )
			
			tuneRFC( data[participantId][task], outputFilename )
			
	# Calculate and print the elapsed time
	elapsed_time = time.time() - start_time
	print( "Elapsed time: " + str(elapsed_time) )
		
	

def tuneRFC( data, outputFilename ):
	"""
		Tune random forest classifier using grid search across the 
		various parameter options, writing the most successful model information 
		out to the specified file
	"""
	
	# Cut off header information
	data = data[1:]
	
	# Cast to numpy array and split
	npData = array( data )
	features = npData[:,:-1].astype( np.float_ )
	labels = npData[:,-1]
	
	# Initialize max holder
	bestModelPara = {}
	bestModelPerf = { 'accuracy':0 }
	
	numTrees = [ 150, 300, 500, 750, 1000 ]
	maxDepths = [ 100, 200, 300, 400, 500 ]
	
	for numTree in numTrees:
		for maxDepth in maxDepths:
			performance = trainAndEvaluateRFC( features, labels, numTree, maxDepth )
			if performance[0] > bestModelPerf['accuracy']:
				bestModelPara['numTrees'] = numTree
				bestModelPara['maxDepth'] = maxDepth

				
				bestModelPerf['accuracy'] = performance[0]
				bestModelPerf['report'] = performance[1]
			
			# Print a dot each time a cycle has finished for a visualization that
			# it has not hung.
			print('.')
	
	writeData( bestModelPara, bestModelPerf, outputFilename ) 					
	

def trainAndEvaluateRFC( features, labels, numTrees, maxDepth ):
	"""
		Train and evaluate a random forest classifier on the given features
		with the given attributes. 3-fold cross-validation is used
		one each run, the average accuracy, precision, recall, and fmeasure
		of all three folds is returned. 
	"""
	
	# Create 3-fold cross validation indices
	skf = cross_validation.StratifiedKFold( labels )
	encoder = LabelEncoder()
	
	accuracySum = 0
	totalResults = []
	totalTargets = []
	
	# For each k-fold split
	for trainIndex, testIndex in skf:
		# Get data split
		featuresTrain, featuresTest = features[trainIndex], features[testIndex]
		labelsTrain, labelsTest = labels[trainIndex], labels[testIndex]
		
		# Train the neural network
		rfc = trainRFC( featuresTrain, labelsTrain, numTrees, maxDepth, encoder )
		
		# Evaluate ANN on test data
		accuracy, outputLabels = evaluateRFC( featuresTest, labelsTest, rfc, encoder )
		
		accuracySum += accuracy
		
		# Store the results / targets for larger analysis
		totalResults.extend( outputLabels.tolist() )
		totalTargets.extend( labelsTest.tolist() )
		
	# Generate performance report
	report = classification_report( totalTargets, totalResults )
	
	return ( accuracySum / 3.0, report )
		
		
		
def trainRFC( features, labels, numTrees, maxDepth, encoder ):
	"""
		Train the random forest using the given training data and 
		parameters. Returns a fully trained random forest.
	"""
	
	# Binarize labels
	labels = encoder.fit_transform( labels )
	
	# Cast numpy to python list
	rfcFeatures = features.tolist()
	rfcLabels = labels.tolist()
	
	# Create the random forest, parallelizing across 7 jobs
	rfc = RandomForestClassifier( n_estimators=numTrees, max_depth=maxDepth, n_jobs=7 )
	
	# Train the RFC
	rfc.fit( rfcFeatures, rfcLabels )
	
	return rfc
	
def evaluateRFC( features, targets, rfc, encoder ):
	"""
		Evaluate the RFC on the given test data. The accuracy of the model
		is returned as well as the targets / pred for further analysis.
	"""
	
	rfcFeatures = features.tolist()
	
	# Classify each entry in rfcFeatures using the rfc
	output = rfc.predict( rfcFeatures )
		
	outputLabels = encoder.inverse_transform( output )

	accuracy = accuracy_score( targets, outputLabels )
	
	return accuracy, outputLabels
		
def writeData( parameters, performance, outputFilename ):
	"""
		Write performance data and parameters of best model
		out to a file.
	"""
	
	with safe_open( outputFilename, 'w' ) as fout:
		fout.write( "Performance:\n")
		fout.write( "\tAccuracy: " + str( performance['accuracy'] ) + '\n' )
		fout.write( "\n" )
		fout.write( performance['report'] + '\n' )
		
		fout.write( '\n\n' )
		
		fout.write( "Parameters:\n")
		fout.write( "\tNumber of Trees: " + str( parameters['numTrees'] ) + '\n' )
		fout.write( "\tMax Depth: " + str( parameters['maxDepth'] ) + '\n' )

		
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
	
	
if __name__ == '__main__':
	main()
