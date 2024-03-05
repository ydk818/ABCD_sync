import os
import scipy.io
import pandas as pd
import numpy as np

class Subject():
    '''Utility to help process subjects files'''

    def __init__(self, file_path, raw_data_dr, c_save_dr, t_save_dr):
        
        # Get subject name from file path
        self.name = file_path.split('/')[-1].split('_')[0]

        # Get loc of subjects dr based on name
        self.dr = os.path.join(raw_data_dr, self.name, 'ses-baselineYear1Arm1', 'func')

        # Save as attrs
        self.c_save_dr = c_save_dr
        self.t_save_dr = t_save_dr

    def save_loc(self, timeseries=True, run='concat'):
        
        # Get right save dr
        s_dr = self.t_save_dr
        if not timeseries:
            s_dr = self.c_save_dr

        run_loc = run
        if run != 'concat':
            run_loc = f'run{run}'

        return os.path.join(s_dr, run_loc, f'{self.name}.npy')

    def get_base_confounds_df(self, run='concat'):

        if run == 'concat':
            return pd.concat([self.get_base_confounds_df(run=1),
                              self.get_base_confounds_df(run=2)])

        # Get motion, csf and wm dfs then concat
        motion_df = self.get_motion_df(run)
        csf_df = self.get_csf_df(run)
        wm_df = self.get_wm_df(run)

        return pd.concat([motion_df, csf_df, wm_df], axis=1)

    def check_all_exists(self):
        
        # All loc funcs
        run_funcs = [self.get_motion_loc,
                     self.get_csf_loc,
                     self.get_mw_loc,
                     self.get_mot_loc]

        # If any missing return False
        for run in ['1', '2']:
            for func in run_funcs:
                if not os.path.exists(func(run)):
                    return False
        
        # All exist, return True
        return True

    def get_motion_loc(self, run):
        return os.path.join(self.dr, f'{self.name}_ses-baselineYear1Arm1_task-nback_run-{run}_desc-filteredincludingFD_motion.tsv')

    def get_motion_df(self, run):

        # Load data from saved file
        df = pd.read_csv(self.get_motion_loc(run), delimiter=' ')
        
        # Keep 12 motion regressors
        to_keep = ['trans_x_mm', 'trans_y_mm', 'trans_z_mm', 'rot_x_degrees', 'rot_y_degrees',
                   'rot_z_degrees', 'trans_x_mm_dt', 'trans_y_mm_dt', 'trans_z_mm_dt',
                   'rot_x_degrees_dt', 'rot_y_degrees_dt', 'rot_z_degrees_dt']

        return df[to_keep]
    
    def get_csf_loc(self, run):
        return os.path.join(self.dr, f'{self.name}_ses-baselineYear1Arm1_task-nback_run-{run}_csf_timeseries.tsv')

    def get_csf_df(self, run):

        df = pd.read_csv(self.get_csf_loc(run), delimiter='\t', names=['csf'], dtype='float')
        return df['csf']

    def get_mw_loc(self, run):
        return os.path.join(self.dr, f'{self.name}_ses-baselineYear1Arm1_task-nback_run-{run}_wm_timeseries.tsv')

    def get_wm_df(self, run):

        df = pd.read_csv(self.get_mw_loc(run) , delimiter='\t',names=['wm'],dtype='float')
        return df['wm']

    def get_mot_loc(self, run=None):
        return os.path.join(self.dr, f'{self.name}_ses-baselineYear1Arm1_task-nback_desc-filteredwithoutliers_motion_mask.mat')

    def get_dummy_df(self, df_index):
        
        # Load censor from .mat
        loc = self.get_mot_loc()
        censor = np.squeeze(scipy.io.loadmat(loc)['motion_data'][0][20][0][0][3])

        # Gen dummy matrix
        dummy = np.zeros((len(censor), len(censor)))
        for i, val in enumerate(censor):
            dummy[i, i] = val
        
        # Get as df
        df_dummy = pd.DataFrame(dummy, index=df_index)
    
        # Drop all 0 cols
        df_dummy = df_dummy.loc[:, (df_dummy!= 0).any(axis=0)]

        return df_dummy

    def get_confounds_df(self):
        
        # Get base motion, dsf, wm confounds
        base_confounds_df = self.get_base_confounds_df(run='concat')

        # Get Censoring Signal Dummy Coded
        dummy_df = self.get_dummy_df(base_confounds_df.index)

        # Concat
        confounds_df = pd.concat([base_confounds_df, dummy_df],axis=1)

        return confounds_df
