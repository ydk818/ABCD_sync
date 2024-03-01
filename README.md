# ABCD_sync
This repository is the NERVE Lab's modified ABCD Data History from 2.0 (Baseline), 4.0 (Year 1), and 6.0 (Year 2).



##1. Baseline (2.0)

Raw:

Modified
Images
DAIRC
/gpfs2/scratch/acjulian/ABCD_HCP_BIDS/DAIRC_ROI_data/tsv_files/baseline_year_1_arm_1
DCAN(dtseries)
NBack (ABCD_hcp_pipelne)
/gpfs2/scratch/Julian/ABCD_HCP_BIDS/nback_dtseries
Connectivity

3.0
NDA 
/gpfs2/scratch/acjulian/ABCD_HCP_BIDS/ABCDStudyNDAr3

4.0 Year-Two
Task fMRI
/gpfs2/scratch/acjulian/ABCD_HCP_BIDS/DAIRC_ROI_data/tsv_files/2_year_follow_up_y_arm_1

The original HCP Pipelines is a set of tools (primarily, but not exclusively, shell scripts) for processing MRI images for the Human Connectome Project, as outlined in Glasser et al. 2013. The original pipeline software is available here

In particular, the DCAN labs repository includes several modifications of primary shell scripts for processing functional MRI data.

The changes include:

updating the nonlinear registration tool to ANTs
using denoising and N4BiasCorrection to increase consistency over extreme noise or bias in anatomical scans
optional processing with no T2-weighted image
adjusting the order of some image processing operations
several additional options for processing
This is the backend component for the processing of data. It is not designed for direct use as a user interface. For the pipeline interface in the form of a dockerized bids application, please refer to the official application repository.
