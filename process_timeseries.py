import os
import sys
import glob
import random
import time

from subj import Subject
from funcs import (get_parcel_extractor, proc_and_save,
                   run_clean, proc_rois, load_data)

# Base dr is directory where data was downloaded
# Data dr is main directory where to save data
from config import raw_data_dr, data_dr

# First load in passed parcel name
parcel_name = str(sys.argv[1])

# Base behavior is surface
volume = False
nback_glob_path =\
    os.path.join(raw_data_dr, '*/ses-baselineYear1Arm1/func/sub-*_ses-baselineYear1Arm1_task-nback_bold_desc-filtered_timeseries.dtseries.nii')

# If '_volume' in parc, process differently
if '_volume' in parcel_name:
    volume = True
    nback_glob_path =\
        os.path.join(raw_data_dr, '*/ses-baselineYear1Arm1/func/sub-*_ses-baselineYear1Arm1_task-nback_run-1_space-MNI_bold.nii.gz')
    
# Get all locs for nback files
nback_files = glob.glob(nback_glob_path)

# If volume, filter to make sure run1 and run2 are there
if volume:
    nback_files = [file for file in nback_files if os.path.exists(file.replace('run-1', 'run-2'))]

print(f'Found {len(nback_files)} files.')

# Get parcel ROI extractor
extractor = get_parcel_extractor(parcel_name,
                                 ex_file=nback_files[0],
                                 volume=volume)

# Sep save directories for connectomes / timeseries / per roi
c_save_dr = os.path.join(data_dr, 'connectomes', parcel_name)
t_save_dr = os.path.join(data_dr, 'timeseries', parcel_name)

# Make sure save directories initialized
dr_options = ['concat', 'run1', 'run2']

for o in dr_options:
    os.makedirs(os.path.join(c_save_dr, o), exist_ok=True)
    os.makedirs(os.path.join(t_save_dr, o), exist_ok=True)

# Randomize order - useful for multi-proc
random.shuffle(nback_files)

# For each file
for file_path in nback_files:

    # Init subject helper class
    subj = Subject(file_path, raw_data_dr=raw_data_dr,
                   c_save_dr=c_save_dr, t_save_dr=t_save_dr)

    # Check to make sure all files
    # needed exist for this subject
    # otherwise, skip
    if not subj.check_all_exists():
        continue

    # Check if already exists - if so skip
    # Use last processed, which is connectivity run 2
    # as the check, in case a job fails earlier
    if os.path.exists(subj.save_loc(timeseries=False, run='2')):
        continue
    
    start = time.time()
    print(f'Start proc run for {subj.name}', flush=True)
        
    # Get confounds df
    confounds_df = subj.get_confounds_df()

    # Load data next
    data = load_data(file_path, volume=volume)

    # Get data as timeseries rois
    rois = proc_rois(data, extractor)

    # Clean the timeseries rois
    # Also truncates initial frames from rois + confounds
    rois = run_clean(rois, confounds_df)
    
    # Save ROI timeseries and conn matrices
    for run in ['concat', '1', '2']:
        proc_and_save(rois, subj, run=run)

    # Print how long it took
    print(f'Saved in: {time.time() - start}', flush=True)
    


