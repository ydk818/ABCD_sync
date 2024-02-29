# ABCD_sync
This repository is the NERVE Lab's modified ABCD Data History from Baseline, 2.0, 4.0, and 6.0.

The original HCP Pipelines is a set of tools (primarily, but not exclusively, shell scripts) for processing MRI images for the Human Connectome Project, as outlined in Glasser et al. 2013. The original pipeline software is available here

In particular, the DCAN labs repository includes several modifications of primary shell scripts for processing functional MRI data.

The changes include:

updating the nonlinear registration tool to ANTs
using denoising and N4BiasCorrection to increase consistency over extreme noise or bias in anatomical scans
optional processing with no T2-weighted image
adjusting the order of some image processing operations
several additional options for processing
This is the backend component for the processing of data. It is not designed for direct use as a user interface. For the pipeline interface in the form of a dockerized bids application, please refer to the official application repository.
