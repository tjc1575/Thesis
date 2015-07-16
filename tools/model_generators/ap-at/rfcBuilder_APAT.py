#!/usr/local/bin/python3
"""
	Filename: rfcBuilder_APAT.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Generate random forest classifier models for the all participant, all 
	task setup.
"""

import pickle
import errno
import time

import numpy as np

from argparse import ArgumentParser
from os import path, makedirs, walk
from os.path import dirname, realpath, basename, normpath

from numpy import array, argmax, zeros, hstack, vstack
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
		
	# Record start time so that the elapsed time can be determined
	start_time = time.time()
	
	outputFilename = path.join( outputDirectory, 'all.txt' )
	tuneRFC( data, outputFilename )
			
	# Calculate and print the elapsed time
	elapsed_time = time.time() - start_time
	print( "Elapsed time: " + str(elapsed_time) )
		
def compileData( features, labels ):
	"""
		Create 3 fold cross validation data for each
		participant and each task and then combine them into one dataset
	"""
	
	# Sort keys to ensure they are in the same order every run
	participantIds = sorted(list(labels.keys()))
	
	# Create 3-fold cross validation indices for each participant for matb
	skfListMATB = []
	for participantId in participantIds:
		skfListMATB.append( cross_validation.StratifiedKFold( labels[participantId]['matb'] ) )
		
	# Create 3-fold cross validation indices for each participant for rantask
	skfListRantask = []
	for participantId in participantIds:
		skfListRantask.append( cross_validation.StratifiedKFold( labels[participantId]['rantask'] ) )
		
	# Combine fold data. Outer list is one for each fold, 
	# each fold contains four lists, training features, training labels
	# testing features, testing labels 
	combinedData = [ [ [], [], [], [] ], [ [], [], [], [] ], [ [], [], [], [] ] ]
		
	
	# Initialize the combinedData list with data from the first participant for matb
	index = 0
	pId = participantIds[0]
	for trainIndex, testIndex in skfListMATB[ 0 ]:
		featuresTrain, featuresTest = features[pId]['matb'][trainIndex], features[pId]['matb'][testIndex]
		labelsTrain, labelsTest = labels[pId]['matb'][trainIndex], labels[pId]['matb'][testIndex]
		
		combinedData[index][0] = featuresTrain
		combinedData[index][1] = labelsTrain
		combinedData[index][2] = featuresTest
		combinedData[index][3] = labelsTest
		
		index += 1
	
	# Append the data from the rest of the participants for matb
	for pIndex in range( 1, len( participantIds ) ):
		index = 0
		pId = participantIds[pIndex]
		for trainIndex, testIndex in skfListMATB[ pIndex ]:
			featuresTrain, featuresTest = features[pId]['matb'][trainIndex], features[pId]['matb'][testIndex]
			labelsTrain, labelsTest = labels[pId]['matb'][trainIndex], labels[pId]['matb'][testIndex]
			
			combinedData[index][0] = vstack((combinedData[index][0], featuresTrain ))
			combinedData[index][1] = hstack((combinedData[index][1], labelsTrain ))
			combinedData[index][2] = vstack((combinedData[index][2], featuresTest ))
			combinedData[index][3] = hstack((combinedData[index][3], labelsTest ))
			
			index += 1
			
	# Append the data from the participants for rantask
	for pIndex in range( len( participantIds ) ):
		index = 0
		pId = participantIds[pIndex]
		for trainIndex, testIndex in skfListRantask[ pIndex ]:
			featuresTrain, featuresTest = features[pId]['rantask'][trainIndex], features[pId]['rantask'][testIndex]
			labelsTrain, labelsTest = labels[pId]['rantask'][trainIndex], labels[pId]['rantask'][testIndex]
			
			combinedData[index][0] = vstack((combinedData[index][0], featuresTrain ))
			combinedData[index][1] = hstack((combinedData[index][1], labelsTrain ))
			combinedData[index][2] = vstack((combinedData[index][2], featuresTest ))
			combinedData[index][3] = hstack((combinedData[index][3], labelsTest ))
			
			index += 1
		
	return combinedData

def tuneRFC( data, outputFilename ):
	"""
		Tune random forest classifier using grid search across the 
		various parameter options, writing the most successful model information 
		out to the specified file
	"""
	
	# Cast to numpy array and split
	combinedFeatures = {}
	combinedLabels = {}

	for participant, pData in data.items():
		combinedFeatures[participant] = {}
		combinedLabels[participant] = {}
		for task, tData in pData.items():
			npData = array( tData )
			combinedFeatures[participant][task] = npData[:,:-1].astype( np.float_ )
			combinedLabels[participant][task] = npData[:,-1]
	
	# Perform data combination and 3Fold splitting once for all parameters
	# to save on computations
	combinedData = compileData( combinedFeatures, combinedLabels )
	
	# Initialize max holder
	bestModelPara = {}
	bestModelPerf = { 'accuracy':0 }
	
	numTrees = [ 750, 1000, 1500, 2000, 3000, 4000, 5000 ]
	maxDepths = [ 300, 400, 500, 600, 700, 800, 900, 1000 ]
	
	for numTree in numTrees:
		for maxDepth in maxDepths:
			performance = trainAndEvaluateRFC( combinedData, numTree, maxDepth )
			if performance[0] > bestModelPerf['accuracy']:
				bestModelPara['numTrees'] = numTree
				bestModelPara['maxDepth'] = maxDepth

				
				bestModelPerf['accuracy'] = performance[0]
				bestModelPerf['report'] = performance[1]
			
			# Print a dot each time a cycle has finished for a visualization that
			# it has not hung.
			print('.')
	
	writeData( bestModelPara, bestModelPerf, outputFilename ) 					
	

def trainAndEvaluateRFC( combinedData, numTrees, maxDepth ):
	"""
		Train and evaluate a random forest classifier on the given features
		with the given attributes. 3-fold cross-validation is used
		on each run, the average accuracy, precision, recall, and fmeasure
		of all three folds is returned. 
	"""
	
	encoder = LabelEncoder()
	
	accuracySum = 0
	totalResults = []
	totalTargets = []
	
	# For each k-fold split
	for split in combinedData:
		
		# Get data split
		featuresTrain, featuresTest = split[0], split[2]
		labelsTrain, labelsTest = split[1], split[3]
		
		
		# Train the random forest
		rfc = trainRFC( featuresTrain, labelsTrain, numTrees, maxDepth, encoder )
		
		# Evaluate RFC on test data
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