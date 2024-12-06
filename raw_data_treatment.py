# -*- coding: utf-8 -*-
"""
Short script to process some reflectivity data obtained at the X-ray Fluorescence
(IAEA) at Elettra Sincrotrone. TODO: lots of space for improvement, for example
to add a low value cut for theta data
"""

__author__ = "Juan Reyes-Herrera"
__contact__ = "juan.reyesherrera@elettra.eu"
__licence__ = "MIT"
__copyright__ = "Elettra Sincrotrone Trieste, Italy"
__date__ = "20/11/2024"
__version__ = "0.0.1"

import numpy as np
import h5py
import matplotlib.pyplot as plt


def get_data_from_h5(date, file_name, detector='diode'):

    """ This function reads the target values form the H5 files
    it has the two options for the detectors = 'diode' or 'amptek' 
    """ 
    #creates the prefix that is used inside the 
    prefix = f"Run{date}" +" "+ f"{file_name}"    
    prefix = prefix.replace('.h5','')    
    print(prefix)
    
    #Please check this because there where some changes in the names files,
    # but not internally

    if 'sam5' in file_name:
    
        with h5py.File(file_name, "r") as f:
        
            run = [key for key in f.keys()][0]
            
            if 'sam5' not in run:
                print("""File has a wrong sample name
                      Therefore we change sam5 to sam4 to read it
                      """)
                prefix = prefix.replace('sam5','sam4')

            else:
                print("File_name corresponds to Run name")      
        
    try:
        
        if detector == 'diode':
            
            print("Reading for diode")
            with h5py.File(file_name, "r") as h5file:
           
                theta = np.array(h5file[f'{prefix}/Measurement/TransientScalarData/Theta'])
                signal = np.array(h5file[f'{prefix}/Measurement/TransientVectorData/DIODE'])
                
            print("Success: we have the diode data") 
            print(f"Theta shape: {theta.size}")
            print(f"Signal shape: {signal.size}")
        
        elif detector == 'amptek': 
        
            print("Reading for Amptek")
            with h5py.File(file_name, "r") as h5file:
           
                theta = np.array(h5file[f'{prefix}/Measurement/TransientScalarData/Theta'])
                signal = np.array(h5file[f'{prefix}/Measurement/TransientScalarData/Amptek#1-ROI-2'])
                
            print("Success: we have the Amptek data")    
            print(f"Theta shape: {theta.size}")
            print(f"Signal shape: {signal.size}")
            
    except:
        print("Something went wrong while reading the h5 file please check the file names and date" )

    return theta, signal
    
    
def correcting(diode_theta, diode_signal, amptek_theta, amptek_signal,
               cor_factor=3.05e07, plot_compare=True):
    
    """ This function allows the user to correct the diode signal by a
        correction factor (cor_factor) and compare both signals by a plot. """
    
    #correction
    diode_cor_signal = diode_signal * cor_factor    
    
    if plot_compare:
    
        plt.plot(diode_theta, diode_cor_signal, label='Diode')
        
        plt.plot(amptek_theta, amptek_signal, label='Amptek')
    
        plt.yscale("log")
        plt.xlabel("Theta (Degrees)")
        plt.ylabel("Reflectivity (a.u.)")
    
        #plt.ylimit(1e3, 1e9)
    
        plt.legend()    
        plt.show()
    
    return diode_cor_signal
    
def save_full_data(diode_theta, diode_cor_signal, amptek_theta, amptek_signal,
                  diode_theta_limit = 0.5, plot_full=True, save_file=None):
                  
    """ This function slices the diode_theta by the limit defined by the user, then
    it slices as well the diode signal and concatenates both with the Amptek
    values, allways considering the theta zero. Optionally can plot the final 
    values and save the file by given a name (str) instead of using None, for example:
    "outout_file.csv"
    
    """
    
    #cutting diode theta
    #getting index of value smaller than 0.5 (corrected)
    #we use the first scanning value from the diode as theta zero
    
    theta_zero = diode_theta[0]
    cut_indx = np.argwhere((diode_theta - theta_zero) < diode_theta_limit)[-1][0]       
    
    #here we get the new corrected values (2 theta) 
    two_theta = 2 * np.concatenate((diode_theta[ : cut_indx], amptek_theta - theta_zero), axis=None)
    
    full_signal = np.concatenate((diode_cor_signal[ : cut_indx], amptek_signal), axis=None)    
    
    #to plot    
    if plot_full:
    
        plt.plot(two_theta, full_signal, label="Diode + Amptek")
        plt.legend()
        plt.yscale("log")
        #plt.xlim(0, 5)
        #plt.ylim(0, 1e8)
        plt.xlabel("Corrected 2 Theta (Degrees)")
        plt.ylabel("Reflectivity (a.u.)")
        plt.show()
        
    #to save the values in a file
    if save_file != None:
    
        a = np.vstack((two_theta, full_signal)).T
        np.savetxt(save_file, a, delimiter=",")
        
        print(f"File {save_file} has been save to disk")
    
if __name__ == "__main__":
    
    diode_theta, diode_signal = get_data_from_h5("20241119", "154554_sam2nonAgCl.h5",
                                                 detector='diode')   
    
    amptek_theta, amptek_signal = get_data_from_h5("20241119", "184028_AgCl_notirr.h5",
                                                detector='amptek')

    diode_cor_signal = correcting(diode_theta, diode_signal, amptek_theta,
                                  amptek_signal, cor_factor=3.05e07,
                                  plot_compare=True)

    save_full_data(diode_theta, diode_cor_signal, amptek_theta, amptek_signal,
                  plot_full=True, save_file="output.csv") 
                