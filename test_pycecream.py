import pycecream
import glob
import numpy as np
import os

'''
preprocessing tasks
'''
filter_wavelengths = {'g':4770,'i':7625}


'''
load masses from 'sdssrm_masses.txt'
'''
default_bh_mass = 1.e8
sdssrm_masses = np.loadtxt('sdssrm_masses.txt',skiprows = 1, delimiter = ',')




'''
load data from group 1 folder
'''
input_lightcurve_dir = './example_data'
group_dir = 'group1'
batch_directory = input_lightcurve_dir+'/'+group_dir
pycecream_output_dir = './pycecream_results'

'''
create directory to save pycecream results
'''
if os.path.isdir(pycecream_output_dir+'/'+group_dir) is False:
    os.system('mkdir '+pycecream_output_dir+'/'+group_dir)

'''
loop through targets in current group and run pycecream fits
'''
targets = glob.glob(batch_directory+'/*')
for target in targets:

    '''
    identify rmid
    '''
    idxrmid = target.find('/rm')
    rmid = int(target[idxrmid+3:idxrmid+6])

    '''
    extract lightcurve filenames and wavelengths
    '''
    lightcurve_files = glob.glob(target+'/*.dat')
    lightcurve_files = [f.replace(target+'/','') for f in lightcurve_files]
    wavelength_list = []
    for lcf in lightcurve_files:
        idxrmid = lcf.find('_rm')
        filter = lcf[idxrmid+7]
        wavelength_list.append(filter_wavelengths[filter])

    '''
    sort by increasing wavelength (should already be sorted)
    '''
    idxsort = np.argsort(wavelength_list)
    wavelength_list = [wavelength_list[idx] for idx in idxsort]
    lightcurve_files = [lightcurve_files[idx] for idx in idxsort]

    '''
    instantiate pycecream
    '''
    pcfit = pycecream.pycecream()

    '''
    customize for current target (set output directory and bh mass)
    '''
    pcfit.project_folder = pycecream_output_dir+'/'+group_dir+'/'+target.replace(batch_directory+'/','')
    idx_bh_mass = np.where(sdssrm_masses[:,0] == rmid)[0]
    if len(idx_bh_mass) > 0:
        pcfit.bh_mass = sdssrm_masses[idx_bh_mass[0],1]
    else:
        pcfit.bh_mass = default_bh_mass

    '''
    iteratively add each lightcurve
    '''
    previous_wavelength = -999
    for wavelength, file in zip(wavelength_list, lightcurve_files):
        dat = np.loadtxt(target+'/'+file)
        if wavelength == previous_wavelength:
            pcfit.add_lc(dat, name=file.replace('.dat', ''), share_previous_lag = True)
        else:
            pcfit.add_lc(dat, name=file.replace('.dat', ''), share_previous_lag = False)
        previous_wavelength = wavelength

    '''
    specify the numnber of MCMC iterations. Normally at least several thousand are necessary but shorter numbers 
    can be used just to check everything is working is done here.
    '''
    pcfit.N_iterations = 40

    '''
    specify the step sizes for the fit parameters. 
    Here we are setting the accretion rate step size to vary by ~ 0.1 solar masses per year.
    '''
    pcfit.p_accretion_rate, pcfit.p_accretion_rate_step = [0.1, 0.1]
    pcfit.p_inclination, pcfit.p_inclination_step = [0.0, 0.0]


    '''
    Check the input settings are ok prior to running
    '''
    print(pcfit.lightcurve_input_params)

    '''
    RUN! specify ncores (default = 1) to parallelise with 1 chain per core
    '''
    #pcfit.run(ncores=4)


    '''
    the rest goes as following the readme file in https://github.com/dstarkey23/pycecream
    '''











