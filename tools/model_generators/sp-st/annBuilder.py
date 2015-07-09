#!/usr/local/bin/python3
"""
	Filename: annBuilder.py
	Author: Taylor Carpenter <tjc1575@rit.edu>
	Generate neural network models for the same participant, same 
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
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from fann2 import libfann

from multiprocessing import Process
		
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
		processes = []
		for participantId in participantIds:
			outputFilename = path.join( outputDirectory, participantId + '-' + task + '.txt' )
			
			# Spin off a process for the building
			processes.append( Process( target=tuneANN, 
				args=( data[participantId][task], outputFilename ) ) )
			processes[-1].start()
			exit()
		
		# Wait for all threads to finish before starting the next task
		for process in processes:
			process.join()
			
	# Calculate and print the elapsed time
	elapsed_time = time.time() - start_time
	print( "Elapsed time: " + str(elapsed_time) )
		
	

def tuneANN( data, outputFilename ):
	"""
		Tune ANN using grid search across the various parameter options,
		writing the most successful model information out to the 
		specified file
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
	
	connRates = [ 0.7 ]#, 0.9, 1.0 ]
	hidNodes = [ 72 ]#, 50, 35 ]
	errors = [ 0.01 ]#, 0.001, 0.0005 ]
	
	for connRate in connRates:
		for hidNode in hidNodes:
			for error in errors:
				performance = trainAndEvaluateANN( features, labels, connRate,
					hidNode, error )
				if performance[0] > bestModelPerf['accuracy']:
					bestModelPara['connRate'] = connRate
					bestModelPara['hidNode'] = hidNode
					bestModelPara['error'] = error

					
					bestModelPerf['accuracy'] = performance[0]
					bestModelPerf['precision'] = performance[1]
					bestModelPerf['recall'] = performance[2]
					bestModelPerf['fmeasure'] = performance[3]
	
	writeData( bestModelPara, bestModelPerf, outputFilename ) 					
	

def trainAndEvaluateANN( features, labels, connRate, hidNodes, error ):
	"""
		Train and evaluate a neural network on the given features
		with the given attributes. 3-fold cross-validation is used
		one each run, the average accuracy, precision, recall, and fmeasure
		of all three folds is returned. 
	"""
	
	# Create 3-fold cross validation indices
	skf = cross_validation.StratifiedKFold( labels )
	binary = LabelBinarizer()
	
	accuracySum = 0
	precisionSum = 0
	recallSum = 0
	fmeasureSum = 0
	
	# For each k-fold split
	for trainIndex, testIndex in skf:
		# Get data split
		featuresTrain, featuresTest = features[trainIndex], features[testIndex]
		labelsTrain, labelsTest = labels[trainIndex], labels[testIndex]
		
		# Train the neural network
		ann = trainANN( featuresTrain, labelsTrain, connRate, hidNodes, error, binary )
		
		# Evaluate ANN on test data
		accuracy, precision, recall, fmeasure = evaluateANN( featuresTest, labelsTest, ann, binary )
		
		accuracySum += accuracy
		precisionSum += precision
		recallSum += recall
		fmeasureSum += fmeasure
	
	return ( accuracySum / 3.0, precisionSum / 3.0, recallSum / 3.0, fmeasureSum / 3.0 )
		
		
		
def trainANN( features, labels, connRate, hidNodes, error, binary ):
	"""
		Train the neural network using the given training data and 
		parameters. Returns a fully trained ANN.
	"""
	# Organize ANN parameters
	connection_rate = connRate
	num_input = 72
	num_hidden = hidNodes
	num_output = 3
	desired_error = error
	max_iterations = 100000
	
	# Print out two reports for every ANN
	iterations_between_reports = 50000
	
	# Binarize labels as it is necessary for ANN
	labels = binary.fit_transform( labels )
	
	# Cast numpy to python list
	annFeatures = features.tolist()
	annLabels = labels.tolist()
	
	# Create an ANN training data instance and set data
	training = libfann.training_data()
	training.set_train_data( annFeatures, annLabels )
	
	ann = libfann.neural_net()
	
	ann.create_sparse_array( connection_rate, (num_input, num_hidden, num_output) )
	
	# Train the ANN
	ann.train_on_data( training, max_iterations, iterations_between_reports, desired_error )
	
	return ann
	
def evaluateANN( features, targets, ann, binary ):
	"""
		Evaluate the ANN on the given test data. The accuracy of the model
		as well as the average precision, recall, and fmeasure are returned.
	"""
	
	annFeatures = features.tolist()
	
	# Classify each entry in annFeatures using the ann
	output = []
	for i in range(len(annFeatures)):
	    result =  array( ann.run( annFeatures[i] ) )
	    on = argmax(result)
	    x = zeros((1,3))
	    x[0,on] = 1
	    output.append( x )
	
	for i in range( len(output) ):
		output[i] = binary.inverse_transform( output[i] )

	
	outputLabels = array( output )
	accuracy = accuracy_score( targets, outputLabels )
	precision = precision_score( targets, outputLabels, average='macro' )
	recall = recall_score( targets, outputLabels, average='macro' )
	fmeasure = f1_score( targets, outputLabels, average='macro' )
	
	return accuracy, precision, recall, fmeasure
		
def writeData( parameters, performance, outputFilename ):
	"""
		Write performance data and parameters of best model
		out to a file.
	"""
	
	with safe_open( outputFilename, 'w' ) as fout:
		fout.write( "Performance:\n")
		fout.write( "\tAccuracy: " + str( performance['accuracy'] ) + '\n' )
		fout.write( "\tPrecision: " + str( performance['precision'] ) + '\n' )
		fout.write( "\tRecall: " + str( performance['recall'] ) + '\n' )
		fout.write( "\tF-Measure: " + str( performance['fmeasure'] ) + '\n' )
		
		fout.write( '\n\n' )
		
		fout.write( "Parameters:\n")
		fout.write( "\tConnection Rate: " + str( parameters['connRate'] ) + '\n' )
		fout.write( "\tHidden Layer Nodes: " + str( parameters['hidNode'] ) + '\n' )
		fout.write( "\tDesired Error Rate: " + str( parameters['error'] ) + '\n' )
		
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
