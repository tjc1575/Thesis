#!/usr/local/bin/python3
"""
	Filename: rfcBuilder_CPST.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Generate random forest classifier models for the cross participant, same 
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
		Build all the models. RFC models are built sequentially because
		each one is trained using multiple cores.
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
	
	# Cut off first row header for each data set
	for task in tasks:
		for participantId in participantIds:
			data[participantId][task] = data[participantId][task][1:] 
			
	splits = performSplit( data )
	
	# Record start time so that the elapsed time can be determined
	start_time = time.time()
	
	# Build models for participants in a task
	for task in tasks:
		for participantId in participantIds:
			outputFilename = path.join( outputDirectory, 'testingOn-' + participantId + '-' + task + '.txt' )
			
			tuneRFC( splits[participantId][task], outputFilename )
			
	# Calculate and print the elapsed time
	elapsed_time = time.time() - start_time
	print( "Elapsed time: " + str(elapsed_time) )
		
def performSplit( data ):
	"""
		Perform data split, returning a list of training / test sets.
	"""	
	splits = {}
	
	participants = sorted( list( data.keys() ) )
	tasks = sorted( list( data[participants[0]].keys() ) )
	
	# For each participant to be tested on
	for tParticipant in participants:
		splits[tParticipant] = {}
		for task in tasks:
			splits[tParticipant][task] = { 'train':[], 'test':[]}
			for participant in participants:
				if participant != tParticipant:
					splits[tParticipant][task]['train'].extend( data[participant][task] )
				else:
					splits[tParticipant][task]['test'].extend( data[participant][task] )
					
	return splits

def tuneRFC( data, outputFilename ):
	"""
		Tune random forest classifier using grid search across the 
		various parameter options, writing the most successful model information 
		out to the specified file
	"""
	
	# Cast to numpy array and split
	npDataTrain = array( data['train'] )
	featuresTrain = npDataTrain[:,:-1].astype( np.float_ )
	labelsTrain = npDataTrain[:,-1]
	
	npDataTest = array( data['test'] )
	featuresTest = npDataTest[:,:-1].astype( np.float_ )
	labelsTest = npDataTest[:,-1]
	
	# Initialize max holder
	bestModelPara = {}
	bestModelPerf = { 'accuracy':0 }
	
	numTrees = [ 50, 100, 150, 300, 500, 750, 1000, 1500, 2000 ]
	maxDepths = [ 50, 100, 200, 300, 400, 500, 600, 700, 800 ]
	
	for numTree in numTrees:
		for maxDepth in maxDepths:
			performance = trainAndEvaluateRFC( featuresTrain, labelsTrain, featuresTest, labelsTest, numTree, maxDepth )
			if performance[0] > bestModelPerf['accuracy']:
				bestModelPara['numTrees'] = numTree
				bestModelPara['maxDepth'] = maxDepth

				
				bestModelPerf['accuracy'] = performance[0]
				bestModelPerf['report'] = performance[1]
			
			# Print a dot each time a cycle has finished for a visualization that
			# it has not hung.
			print('.')
	
	writeData( bestModelPara, bestModelPerf, outputFilename ) 					
	

def trainAndEvaluateRFC( featuresTrain, labelsTrain, featuresTest, labelsTest, numTrees, maxDepth ):
	"""
		Train and evaluate a random forest classifier on the given features
		with the given attributes. The average accuracy, precision, recall, and fmeasure
		of all three folds is returned. 
	"""
	
	encoder = LabelEncoder()
	
	accuracySum = 0
	totalResults = []
	totalTargets = []
	
		
	# Train the random forest
	rfc = trainRFC( featuresTrain, labelsTrain, numTrees, maxDepth, encoder )
	
	# Evaluate rfc on test data
	accuracy, outputLabels = evaluateRFC( featuresTest, labelsTest, rfc, encoder )
	
	accuracySum += accuracy
	
	# Store the results / targets for larger analysis
	totalResults.extend( outputLabels.tolist() )
	totalTargets.extend( labelsTest.tolist() )
		
	# Generate performance report
	report = classification_report( totalTargets, totalResults )
	
	return ( accuracySum, report )
		
		
		
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
	rfc = RandomForestClassifier( n_estimators=numTrees, max_depth=maxDepth, n_jobs=8 )
	
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
