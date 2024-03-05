from nibabel.nifti1 import Nifti1Image
import pandas as pd
import numpy as np
import os
from nilearn.connectome import ConnectivityMeasure
from nilearn.signal import clean
from nilearn.input_data import NiftiLabelsMasker, NiftiMapsMasker
from nilearn.datasets import fetch_atlas_difumo
import nibabel as nib

from neurotools.transform.conv import surf_parc_to_cifti
from neurotools.loading.parcels import load_32k_fs_LR_concat
from neurotools.transform.rois import SurfLabels, SurfMaps
from neurotools.loading import load

from config import data_dr


def get_parcel_extractor(parcel_name, ex_file, volume):

    if not volume:
        return get_surf_parcel_extractor(parcel_name, ex_file)

    # Volumetric case
    p_name = parcel_name.replace('_volume', '')

    if 'difumo' in p_name:
        sz = int(p_name.split('_')[1])
        parcel =  nib.load(fetch_atlas_difumo(dimension=sz)['maps'])

    else:
        raise RuntimeError('Not implemented yet')

    # Return extractor
    return NiftiMapsMasker(parcel, dtype='float32', smoothing_fwhm=None)

def get_surf_parcel_extractor(parcel_name, ex_file):
    '''Load mapper object / parcel, needs
    an example cifti file.'''

    # We will save copy once proc
    parc_save_dr = os.path.join(data_dr, 'parcels')
    parc_save_loc = os.path.join(parc_save_dr, parcel_name + '.npy')

    # Load if exists
    if os.path.exists(parc_save_loc):
        parc = np.load(parc_save_loc)

    else:
        # Load parcel - name from input
        # download if doesn't exist
        parcel = load_32k_fs_LR_concat(parcel_name)

        # Convert parcel into cifti space,
        # by adding subcort roi info
        parc = surf_parc_to_cifti(ex_file, parcel,
                                  add_sub=True, verbose=2)

        # Save a copy of the parc in data -
        # so don't need to re-create each time
        os.makedirs(parc_save_dr, exist_ok=True)
        np.save(parc_save_loc, parc)

    # If static
    if len(parc.shape) == 1:
        return SurfLabels(labels=parc, strategy='mean', vectorize=False)

    # Else prob.
    return SurfMaps(maps=parc, strategy='auto', vectorize=False)

def load_data(file_path, volume):

    # Surface case
    if not volume:
        return load(file_path)

    # If volume, load separate
    run1 = nib.load(file_path)
    affine = run1.affine
    run1 = np.array(run1.get_fdata(), 'float32')
    run2 = np.array(nib.load(file_path.replace('run-1', 'run-2')).get_fdata(), 'float32')
    
    # Concat
    data = np.concatenate([run1, run2], axis=-1)

    # Return as nifti
    return Nifti1Image(data, affine=affine)

def trunc_two_runs_at(data, per_run=362):
    
    aim = per_run * 2

    half = len(data)//2
    to_rm = (len(data) - aim) // 2

    run1, run2 = data[to_rm:half], data[half+to_rm:]
    
    if isinstance(data, pd.DataFrame):
        data = pd.concat([run1, run2])
    else:
        data = np.concatenate([run1, run2])

    return data
    
def run_clean(data, confound_df):

    # Truncate initial frames from both df and data
    data = trunc_two_runs_at(data, per_run=362)
    confound_df = trunc_two_runs_at(confound_df, per_run=362)

    # Gen sessions variables to pass to clean
    runs = np.concatenate([np.zeros(362), np.ones(362)])

    # Run clean
    data = clean(data,
                 runs=runs,
                 detrend=True,
                 confounds=np.array(confound_df),
                 low_pass=None,
                 high_pass=0.008,
                 t_r=0.8,
                 ensure_finite=False)
    
    # Return cleaned data
    return data

def proc_rois(data, extractor):

    # Apply extractor - applying the parcellation
    return extractor.fit_transform(data).astype('float32')

def slice_run(data, run):

    # Get half of data if just one run
    if str(run) == '1':
        return data[:362]
    elif str(run) == '2':
        return data[362:]

    return data

def proc_and_save(rois, subj, run='concat'):

    # Trunc to just run if needed
    rois = slice_run(rois, run)

    # Save as cleaned ROI timeseries
    np.save(subj.save_loc(timeseries=True, run=run),
            rois)

    # Generate basic correlation connectome
    connectivity = ConnectivityMeasure(kind='correlation',
                                       discard_diagonal=False,
                                       vectorize=False)
    con_rois = connectivity.fit_transform([rois]).astype('float32')

    # Save as connectivity matrix
    np.save(subj.save_loc(timeseries=False, run=run),
            con_rois)
