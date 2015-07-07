function ParseEEG(inputFile, outputFile)
%ParseEEG reads in the 14 data channels from an EDF file created from
% 	an Emotiv EPOC+ headset, removes the baseline for each channel
%	and writes the results to a tab-separated text file.

% Add EEGLAB to the path to use its functions
EEGLAB_LOCATION = '/Users/tjc1575/Documents/MATLAB/eeglab13';
addpath(genpath(EEGLAB_LOCATION));

% Load the 14 channels from the EDF file
EEG = pop_biosig(inputFile, 'channels',[3:16] ,'importevent','off');
EEG = eeg_checkset( EEG );

% Remove baseline from each channel by removing the mean of the entire segment
EEG = pop_rmbase( EEG, []);
EEG = eeg_checkset( EEG );

% Write the data to a tab-separated text file, with rows being data entries and channels being columns
pop_export(EEG,outputFile,'transpose','on');