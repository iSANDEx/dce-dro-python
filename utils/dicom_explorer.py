#!/usr/bin/env python
import os
import sys
import glob
import logging
import argparse
import numpy as np
import pydicom as pyd
import pandas as pd


def run_main(dicom_folder):

    changing_attributes = {'file_name': []}
    for dicom_file in dicom_folder:
        dcm_metada = pyd.dcmread(dicom_file, stop_before_pixels=True)
        changing_attributes['file_name'] += [os.path.dirname(dicom_file)]
        dcm_attributes = dcm_metada.dir()
        attributes_list = list(changing_attributes.keys())
        for attribute_name in dcm_attributes:
            if attribute_name in attributes_list:
                changing_attributes[attribute_name].append(dcm_metada[attribute_name].value)
            else:
                changing_attributes[attribute_name] = [dcm_metada[attribute_name].value]
        logging.debug(f'Changing Attributes Dict: {changing_attributes}')
        
    # Create a dataframe and show those field where there are more than one unique value
    # if the field are of different size (e.g. fields that only exist in some files), loop over each one:
    # dicom_df = pd.DataFrame(changing_attributes)
    dicom_df = pd.DataFrame({ key:pd.Series(value) for key, value in changing_attributes.items() })

    for field in dicom_df.columns:
        unique_values = dicom_df[field].dropna().drop_duplicates()

        if len(unique_values) == 1:
            dicom_df.drop(field, axis=1, inplace=True)
            
    print(dicom_df.head())
    
    return dicom_df

def get_dcm_list(abs_path, fext = 'dcm'):

    if os.path.isdir(abs_path):
        logging.debug('OK: Provided path is a valid folder')
        list_of_dcm_files = glob.glob(os.path.join(abs_path,f'*.{fext}'))
        if list_of_dcm_files:
            logging.debug(f'The folder contains {len(list_of_dcm_files)} files to process')
        else:
            logging.error(f'There are no files with extension {fext} in the folder {abs_path}')
    else:
        logging.error(f'Path to folder {path_to_folder} does not exist. Nothing done')
        list_of_dcm_files = []

    return list_of_dcm_files


# Main body
if __name__ == '__main__':
    
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser(description='Script to explore dicom files by looking at their dicom metadata',
                                 epilog='Ready to run the script')
    ap.add_argument('-p', '--path', required=True,
                    help='absolute path to the folder containing the dicom files to explore')
    ap.add_argument('-e', '--fext', required=False, default='dcm',
                    help='If the DICOM files have an extension other than "dcm", it can be provided here')
    args = vars(ap.parse_args())
    
    logging.basicConfig(filename=None, #os.path.join(working_path, conf['logs']['logfile']),
	                    format='%(asctime)s - [%(levelname)s]: %(message)s',
	                    level=20)
    logging.info('Starting the script...')

	# Check the path exist and select only the .dcm (or .FEXT) files:
    path_to_folder = args['path']
    fext = args['fext']
    dcm_list = get_dcm_list(path_to_folder, fext=fext)
    
    if dcm_list:
        dcm_metadata_df = run_main(dcm_list)
        dcm_metadata_df.to_csv(os.path.join(os.getenv('HOME'), 'Data','tmp','dicom_metadata.csv'))
    else:
        logging.error(f'There are no files to process. Bye!')